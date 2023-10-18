import torch
import torch.nn as nn
import torch.nn.functional as F

from tetris_constants import ACTIONS, GRID_WIDTH, GRID_HEIGHT

class DuelingQNetwork(nn.Module):
    def __init__(self):
        super(DuelingQNetwork, self).__init__()
        self.fc1 = nn.Linear(GRID_WIDTH * GRID_HEIGHT, 128)  # assuming your state is the flattened grid
        self.fc2 = nn.Linear(128, 128)

        # Value stream
        self.value_fc = nn.Linear(128, 1)

        # Advantage stream
        self.advantage_fc = nn.Linear(128, len(ACTIONS))

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        value = self.value_fc(x)
        advantage = self.advantage_fc(x)

        # Combine V(s) and A(s, a) to get Q(s, a)
        q_values = value + (advantage - advantage.mean())

        return q_values
