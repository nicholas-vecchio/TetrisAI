import random
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
from torch.cuda.amp import autocast, GradScaler
import os

from qnetwork import DuelingQNetwork
from replay import ReplayMemory, Transition
from tetris_constants import GRID_WIDTH, ACTIONS, BATCH_SIZE

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TARGET_UPDATE = 100

class DQNAgent:
    def __init__(self):
        self.qnetwork = DuelingQNetwork().to(device)
        self.target_network = DuelingQNetwork().to(device)
        self.target_network.load_state_dict(self.qnetwork.state_dict())
        self.optimizer = optim.Adam(self.qnetwork.parameters(), lr=0.001)
        self.memory = ReplayMemory(10000)
        self.batch_size = BATCH_SIZE
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.scaler = GradScaler()

        self.rewards_per_episode = []
        self.total_episode_reward = 0
        self.losses = []
        self.action_counts = {action: 0 for action in ACTIONS}
        self.episode_lengths = []
        
        self.graphs_dir = 'graphs'
        if not os.path.exists(self.graphs_dir):
            os.makedirs(self.graphs_dir)

    def act(self, state):
        if random.random() <= self.epsilon:
            return random.choice(ACTIONS)
        with torch.no_grad():
            state = torch.tensor(state["grid"]).float().view(1, -1).to(device)
            with autocast():  # Enable AMP for inference
                action_values = self.qnetwork(state)
            return ACTIONS[action_values.max(1)[1].item()]

    def step(self, state, action, reward, next_state, done):
        action_index = ACTIONS.index(action)
        self.memory.push(
            torch.tensor(state["grid"], device=device).view(-1),
            action_index,
            torch.tensor([reward], device=device),
            None if done else torch.tensor(next_state["grid"], device=device).view(-1),
            done
        )
        self.total_episode_reward += reward
        self.action_counts[action] += 1  # Count the action taken
        if done:
            self.rewards_per_episode.append(self.total_episode_reward)
            self.episode_lengths.append(len(self.memory))  # Store the episode length
            self.total_episode_reward = 0
        if len(self.memory) > self.batch_size:
            transitions = self.memory.sample(self.batch_size)
            self.learn(transitions)
        if len(self.memory) % TARGET_UPDATE == 0:
            self.target_network.load_state_dict(self.qnetwork.state_dict())

    def learn(self, transitions):
        batch = Transition(*zip(*transitions))
        
        # Create a mask for non-final (not done) states
        non_final_next_states_mask = torch.tensor([s is not None for s in batch.next_state], device=device, dtype=torch.bool)
        non_final_next_states = torch.cat([s.clone().detach().float().view(1, -1) for s in batch.next_state if s is not None]).to(device)
        
        state_batch = torch.cat([s.clone().detach().float().view(1, -1) for s in batch.state]).to(device)
        action_batch = torch.cat([torch.tensor([a], device=device) for a in batch.action]).to(device)
        reward_batch = torch.cat(batch.reward).to(device)
        
        with torch.cuda.amp.autocast():  
            state_action_values = self.qnetwork(state_batch).gather(1, action_batch.view(-1, 1))
            
            # Initialize next_state_values to zeros for the actual batch size
            next_state_values = torch.zeros(len(transitions), device=device)
            
            # Update the Q-values only for the non-final next states.
            with torch.cuda.amp.autocast():
                next_state_values_temp = self.target_network(non_final_next_states).max(1)[0].detach()
            next_state_values[non_final_next_states_mask] = next_state_values_temp.float()

            expected_state_action_values = (next_state_values * self.gamma) + reward_batch
            loss = nn.functional.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
        
        self.optimizer.zero_grad()
        # Use scaler to scale the loss before backpropagation
        self.scaler.scale(loss).backward()
        # Step the optimizer with the scaler
        self.scaler.step(self.optimizer)
        self.scaler.update()

        self.losses.append(loss.item())  # Store the loss value

    def plot_loss(self, episode_number):
        plt.figure(figsize=(10, 5))
        plt.plot(self.losses, label='Loss')
        plt.xlabel('Training Step')
        plt.ylabel('Loss')
        plt.title('Loss Over Time')
        plt.legend()
        filename = f'{self.graphs_dir}/{episode_number}_loss_plot.png'
        plt.savefig(filename)
        plt.close()
        print(f"Loss plot saved as {filename}")

    def plot_epsilon(self, episode_number):
        plt.figure(figsize=(10, 5))
        plt.plot(np.linspace(self.epsilon, self.epsilon_min, len(self.rewards_per_episode)), label='Epsilon')
        plt.xlabel('Episode')
        plt.ylabel('Epsilon')
        plt.title('Epsilon Decay Over Episodes')
        plt.legend()
        filename = f'{self.graphs_dir}/{episode_number}_epsilon_plot.png'
        plt.savefig(filename)
        plt.close()
        print(f"Epsilon plot saved as {filename}")

    def plot_action_distribution(self, episode_number):
        plt.figure(figsize=(10, 5))
        actions, counts = zip(*self.action_counts.items())
        plt.bar(actions, counts, label='Action Distribution')
        plt.xlabel('Action')
        plt.ylabel('Count')
        plt.title('Action Distribution Over All Episodes')
        plt.legend()
        filename = f'{self.graphs_dir}/{episode_number}_action_distribution_plot.png'
        plt.savefig(filename)
        plt.close()
        print(f"Action distribution plot saved as {filename}")

    def plot_episode_length(self, episode_number):
        plt.figure(figsize=(10, 5))
        plt.plot(self.episode_lengths, label='Episode Length')
        plt.xlabel('Episode')
        plt.ylabel('Length')
        plt.title('Episode Length Over Time')
        plt.legend()
        filename = f'{self.graphs_dir}/{episode_number}_episode_length_plot.png'
        plt.savefig(filename)
        plt.close()
        print(f"Episode length plot saved as {filename}")

    def plot_rewards(self, episode_number):
        average_interval = 50

        plt.figure(figsize=(10, 5))
        
        # Plot the raw rewards
        plt.plot(self.rewards_per_episode, label='Rewards')
        
        # Calculate and plot the average rewards
        average_rewards = [np.mean(self.rewards_per_episode[max(0, i-average_interval):i+1]) for i in range(len(self.rewards_per_episode))]
        plt.plot(average_rewards, label=f'Average Reward (last {average_interval} episodes)', linestyle='--')
        
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Reward vs Episode')
        plt.legend()
        
        # Ensure the graphs directory exists
        if not os.path.exists('graphs'):
            os.makedirs('graphs')
        
        filename = f'graphs/{episode_number}_reward_plot.png'
        plt.savefig(filename)
        print(f"Plot saved as {filename}")
        plt.close()