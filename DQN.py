import random
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from torch.cuda.amp import autocast, GradScaler

from qnetwork import DuelingQNetwork
from replay import ReplayMemory, Transition
from tetris_constants import GRID_WIDTH, ACTIONS

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TARGET_UPDATE = 100

class DQNAgent:
    def __init__(self):
        self.qnetwork = DuelingQNetwork().to(device)
        self.target_network = DuelingQNetwork().to(device)
        self.target_network.load_state_dict(self.qnetwork.state_dict())
        self.optimizer = optim.Adam(self.qnetwork.parameters(), lr=0.001)
        self.memory = ReplayMemory(10000)
        self.batch_size = 128
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.scaler = GradScaler()  # Add this for AMP

        self.rewards_per_episode = []
        self.total_episode_reward = 0

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
        if done:
            self.rewards_per_episode.append(self.total_episode_reward)
            self.total_episode_reward = 0
        if len(self.memory) > self.batch_size:
            transitions = self.memory.sample(self.batch_size)
            self.learn(transitions)
        if len(self.memory) % TARGET_UPDATE == 0:
            self.target_network.load_state_dict(self.qnetwork.state_dict())

    def learn(self, transitions):
        batch = Transition(*zip(*transitions))
        
        # Create a mask for non-final (not done) states
        non_final_next_states_mask = torch.tensor(tuple(map(lambda s: s is not None and not s[4], transitions)), device=device, dtype=torch.bool)
        non_final_next_states = torch.cat([s.clone().detach().float().view(1, -1) for s in batch.next_state if s is not None and not s[4]]).to(device)
        
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

        self.epsilon = max(self.epsilon_min, self.epsilon_decay*self.epsilon)


    def rolling_average(self, data, window_size):
        cumsum = [0]
        for i, x in enumerate(data, 1):
            cumsum.append(cumsum[i-1] + x)
            if i >= window_size:
                moving_avg = (cumsum[i] - cumsum[i-window_size]) / window_size
                yield moving_avg

    def plot_rewards(self, rewards, window_size=100):
        plt.figure(figsize=(10, 5))
        plt.plot(rewards, label='Rewards')
        plt.plot(list(self.rolling_average(rewards, window_size)), label=f"Rolling avg (window={window_size})", color='red')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Reward vs Episode')
        plt.legend()
        plt.show()
