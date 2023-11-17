import unittest
from tetris_ai import compute_reward 
from tetris_constants import GRID_WIDTH, GRID_HEIGHT

class TestComputeReward(unittest.TestCase):

    def setUp(self):
        # Initialize an empty grid
        self.empty_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.empty_grid_state = {'grid': [cell for row in self.empty_grid for cell in row]}


    def test_no_lines_no_penalties(self):
        reward = compute_reward(self.empty_grid_state, False, 0)
        self.assertEqual(reward, 0, "Reward should be 0 for no lines and no penalties")

    def test_lines_cleared(self):
        for lines_cleared in range(1, 5):
            expected_reward = 100 * (2 ** lines_cleared - 1)  
            reward = compute_reward(self.empty_grid_state, False, lines_cleared)
            self.assertEqual(reward, expected_reward, f"Reward incorrect for {lines_cleared} lines cleared")

    def test_game_over_penalty(self):
        reward = compute_reward(self.empty_grid_state, True, 0)
        self.assertEqual(reward, -300, "Reward should include game over penalty")

    def test_holes_penalty(self):
        # Create a grid state with a hole
        grid_with_holes = [0] * GRID_WIDTH * GRID_HEIGHT
        grid_with_holes[GRID_WIDTH * (GRID_HEIGHT - 1)] = 1  # Bottom left cell filled
        grid_with_holes[GRID_WIDTH * (GRID_HEIGHT - 2)] = 0  # Cell above is a hole
        grid_state_with_holes = {'grid': grid_with_holes}

        reward = compute_reward(grid_state_with_holes, False, 0)
        expected_penalty = -10  # HOLE_PENALTY for one hole
        self.assertEqual(reward, expected_penalty, "Failed: Reward should include holes penalty of -10 for one hole")

    def test_height_penalty(self):
        # Create a grid state with one block above the height threshold
        grid_with_height = [0] * GRID_WIDTH * GRID_HEIGHT
        threshold_index = GRID_WIDTH * (GRID_HEIGHT // 2 - 1)
        grid_with_height[threshold_index] = 1  # One block just above the height threshold
        grid_state_with_height = {'grid': grid_with_height}

        reward = compute_reward(grid_state_with_height, False, 0)
        expected_penalty = -1  # HEIGHT_PENALTY for one block
        self.assertEqual(reward, expected_penalty, "Failed: Reward should include height penalty of -1 for one block above threshold")

    def test_height_variance_penalty(self):
        # Create a grid state with height variance
        grid_with_variance = [0] * GRID_WIDTH * GRID_HEIGHT
        grid_with_variance[GRID_WIDTH * (GRID_HEIGHT - 1)] = 1  # Bottom left cell filled
        grid_with_variance[GRID_WIDTH * (GRID_HEIGHT - 2) + 1] = 1  # Next column, one cell above
        grid_state_with_variance = {'grid': grid_with_variance}

        reward = compute_reward(grid_state_with_variance, False, 0)
        expected_penalty = -0.3  # HEIGHT_VARIANCE_PENALTY for one unit of variance
        self.assertEqual(reward, expected_penalty, "Failed: Reward should include height variance penalty of -0.3 for one unit of variance")

if __name__ == '__main__':
    unittest.main()