import random
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

from qnetwork import DuelingQNetwork  # Import the new network architecture
from replay import ReplayMemory, Transition

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from tetris_constants import GRID_WIDTH, ACTIONS

TARGET_UPDATE = 100

class DQNAgent:
    def __init__(self):
        self.qnetwork = DuelingQNetwork().to(device)
        self.target_network = DuelingQNetwork().to(device)
        self.target_network.load_state_dict(self.qnetwork.state_dict())
        self.optimizer = optim.Adam(self.qnetwork.parameters(), lr=0.001)
        self.memory = ReplayMemory(10000)
        self.batch_size = 64
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

        # Reward plotting additions
        self.rewards_per_episode = []
        self.total_episode_reward = 0

    def act(self, state):
        if random.random() <= self.epsilon:
            return random.choice(ACTIONS)
        with torch.no_grad():
            state = torch.tensor(state["grid"]).float().view(1, -1).to(device)
            action_values = self.qnetwork(state)
            return ACTIONS[action_values.max(1)[1].item()]

    def step(self, state, action, reward, next_state, done):
        action_index = ACTIONS.index(action)
        self.memory.push(torch.tensor(state["grid"], device=device).view(-1), action_index, torch.tensor([reward], device=device), torch.tensor(next_state["grid"], device=device).view(-1), done)
        
        self.total_episode_reward += reward  # Add rewards
        
        if done:
            self.rewards_per_episode.append(self.total_episode_reward)
            self.total_episode_reward = 0  # Reset episode reward
        
        if len(self.memory) > self.batch_size:
            transitions = self.memory.sample(self.batch_size)
            self.learn(transitions)

        if len(self.memory) % TARGET_UPDATE == 0:
            self.target_network.load_state_dict(self.qnetwork.state_dict())

    def learn(self, transitions):
        batch = Transition(*zip(*transitions))
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool)
        non_final_next_states = torch.cat([s.clone().detach().float().view(1, -1) for s in batch.next_state if s is not None]).to(device)
        state_batch = torch.cat([s.clone().detach().float().view(1, -1) for s in batch.state]).to(device)
        action_batch = torch.cat([torch.tensor([a], device=device) for a in batch.action]).to(device)
        reward_batch = torch.cat(batch.reward).to(device)
        state_action_values = self.qnetwork(state_batch).gather(1, action_batch.view(-1, 1))
        next_state_values = torch.zeros(self.batch_size, device=device)
        next_state_values[non_final_mask] = self.target_network(non_final_next_states).max(1)[0].detach()
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch
        loss = nn.functional.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.epsilon = max(self.epsilon_min, self.epsilon_decay*self.epsilon)
    
    def plot_rewards(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.rewards_per_episode)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Reward vs Episode')
        plt.show()
