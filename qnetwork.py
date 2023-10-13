import torch
import torch.nn as nn

from tetris_constants import ACTIONS, GRID_WIDTH

class QNetwork(nn.Module):
    def __init__(self):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(GRID_WIDTH * GRID_WIDTH, 128)  # Adjust as necessary
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, len(ACTIONS))

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
