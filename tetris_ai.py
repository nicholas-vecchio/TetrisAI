from tetris_pieces import tetrominoes, generate_bag
from tetris_constants import GRID_WIDTH, GRID_HEIGHT
from tetris_grid import is_valid_move, place_tetromino_on_grid

'''def compute_reward(new_state, game_over, lines_cleared):
    reward = 0

    # Constants
    LINE_CLEAR_REWARD = 100
    HOLE_PENALTY = 10
    GAME_OVER_PENALTY = 300
    HEIGHT_THRESHOLD = GRID_HEIGHT // 2
    HEIGHT_PENALTY = 1
    HEIGHT_VARIANCE_PENALTY = 0.3

    new_grid_2d = [new_state['grid'][i:i+GRID_WIDTH] for i in range(0, len(new_state['grid']), GRID_WIDTH)]

    # Exponential award for line clears.
    reward += LINE_CLEAR_REWARD * (2 ** lines_cleared - 1) if lines_cleared > 0 else 0

    # Penalize holes
    holes = sum(1 for x in range(GRID_WIDTH) 
                for y in range(GRID_HEIGHT-1) 
                if new_grid_2d[y][x] and not new_grid_2d[y+1][x])
    reward -= HOLE_PENALTY * holes

    # Penalize height
    blocks_above_threshold = sum(1 for x in range(GRID_WIDTH) for y in range(HEIGHT_THRESHOLD) if new_grid_2d[y][x])
    reward -= HEIGHT_PENALTY * blocks_above_threshold

    # Penalize column height variance
    column_heights = [max([y for y in range(GRID_HEIGHT) if new_grid_2d[y][x]], default=-1) for x in range(GRID_WIDTH)]
    height_variance_penalty = sum(abs(column_heights[i] - column_heights[i+1]) for i in range(GRID_WIDTH - 1))
    reward -= HEIGHT_VARIANCE_PENALTY * height_variance_penalty

    # Game over penalty
    if game_over:
        reward -= GAME_OVER_PENALTY

    return reward
    '''

# Different compute reward for testing
def compute_reward(new_state, game_over, lines_cleared):
    reward = 0

    # Constants
    LINE_CLEAR_REWARD = [0, 5, 25, 50, 100]  # Indexed by number of lines cleared
    HOLE_PENALTY = 0.05
    HEIGHT_PENALTY = 0.02
    BALANCE_REWARD = 0.03
    GAME_OVER_PENALTY = 20
    HEIGHT_THRESHOLD = GRID_HEIGHT // 2
    SURVIVAL_REWARD = 0.1

    new_grid_2d = [new_state['grid'][i:i+GRID_WIDTH] for i in range(0, len(new_state['grid']), GRID_WIDTH)]
    column_heights = [max([y for y in range(GRID_HEIGHT) if new_grid_2d[y][x] != 0] + [0]) for x in range(GRID_WIDTH)]

    # Reward for line clears
    reward += LINE_CLEAR_REWARD[lines_cleared]

    # Penalize holes
    holes = sum(1 for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT - 1) if new_grid_2d[y][x] == 0 and new_grid_2d[y + 1][x] != 0)
    reward -= HOLE_PENALTY * holes

    # Penalize height
    blocks_above_threshold = sum(1 for x in range(GRID_WIDTH) for y in range(HEIGHT_THRESHOLD) if new_grid_2d[y][x])
    reward -= HEIGHT_PENALTY * blocks_above_threshold

    # Reward for balancing the board
    avg_height = sum(column_heights) / GRID_WIDTH
    balance = sum(abs(h - avg_height) for h in column_heights)
    reward += BALANCE_REWARD * (GRID_HEIGHT - balance)

    # Reward for survival
    reward += SURVIVAL_REWARD

    if game_over:
        reward -= GAME_OVER_PENALTY

    return reward


def generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino):    
    # 1. Grid State:
    grid_state = [cell for row in grid for cell in row]

    if len(grid_state) != GRID_WIDTH * GRID_HEIGHT:
            print("[DEBUG] Unexpected grid state shape:", len(grid_state))
        # 2. Current Tetromino State:
    tetromino_type = tetrominoes.index(current_tetromino)
    tetromino_position = (tetromino_x, tetromino_y)
    tetromino_rotation = current_rotation

    # 3. Next Tetromino State:
    next_tetromino_type = tetrominoes.index(next_tetromino)

    # Combine into a single state dictionary
    state = {
        "grid": grid_state,
        "tetromino": current_tetromino,
        "tetromino_type": tetromino_type,
        "tetromino_position": tetromino_position,
        "tetromino_rotation": tetromino_rotation,
        "next_tetromino_type": next_tetromino_type,
        "held_tetromino": held_tetromino
    }

    state["has_held"] = has_held

    return state

def apply_action(tetromino, action, state, next_tetromino, bag):
    """
    Apply a specified action to a tetromino and returns the updated state.
    """
    move, rotation = action

    # Copy current state (you might want to use a deep copy if the state is more complex)
    new_state = state.copy()

    # Rotate the tetromino
    rotated_tetromino = tetromino[rotation]
    if not is_valid_move(rotated_tetromino, state['tetromino_position'][0], state['tetromino_position'][1]):
        rotation = state['tetromino_rotation']  # Revert to the original rotation if the new rotation is invalid

    # Handle different move actions
    if move == 'LEFT':
        if is_valid_move(rotated_tetromino, new_state['tetromino_position'][0] - 1, new_state['tetromino_position'][1]):
            new_state['tetromino_position'] = (new_state['tetromino_position'][0] - 1, new_state['tetromino_position'][1])
    
    elif move == 'RIGHT':
        if is_valid_move(rotated_tetromino, new_state['tetromino_position'][0] + 1, new_state['tetromino_position'][1]):
            new_state['tetromino_position'] = (new_state['tetromino_position'][0] + 1, new_state['tetromino_position'][1])

    elif move == 'HARD_DROP':
        x = new_state['tetromino_position'][0]
        y = new_state['tetromino_position'][1]
        while is_valid_move(rotated_tetromino, x, y + 1):
            y += 1
        new_state['tetromino_position'] = (x, y)

    elif move == 'HOLD':
        # Check if the tetromino has been held during this fall
        if not new_state["has_held"]:
            if new_state['held_tetromino'] is None:
                new_state['held_tetromino'] = tetromino
                tetromino = next_tetromino
                if not bag:
                    bag = generate_bag()
                next_tetromino = bag.pop()
            else:
                new_state['held_tetromino'], tetromino = tetromino, new_state['held_tetromino']

            new_state['tetromino_position'] = (GRID_WIDTH // 2, 0)
            new_state['tetromino_rotation'] = 0
            new_state['tetromino'] = tetromino
            new_state["has_held"] = True 

    new_state['tetromino_rotation'] = rotation

    # Return the new state
    return new_state

# heuristic functions

def number_of_completed_lines(grid):
    return sum(1 for row in grid if all(row))

def count_holes(grid):
    return sum(1 for x in range(GRID_WIDTH) 
                for y in range(GRID_HEIGHT-1) 
                if grid[y][x] and not grid[y+1][x])

def calculate_aggregate_height(grid):
    return sum(y for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if grid[y][x])

def calculate_bumpiness(grid):
    heights = [y for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if grid[y][x]]
    return sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))

def drop_position(grid, tetromino, x):
    for y in range(GRID_HEIGHT):
        if not is_valid_move(tetromino, x, y):
            return y - 1
    return GRID_HEIGHT - 1

def evaluate_move(grid, tetromino, x, rotation):
    y = drop_position(grid, tetromino, x)
    temp_grid = place_tetromino_on_grid(grid, tetromino, x, y, rotation)
    
    completed_lines = number_of_completed_lines(temp_grid)
    holes = count_holes(temp_grid)
    aggregate_height = calculate_aggregate_height(temp_grid)
    bumpiness = calculate_bumpiness(temp_grid)
    
    # Weights can be adjusted based on empirical results or training
    return (-0.5 * aggregate_height + 0.76 * completed_lines - 0.36 * holes - 0.18 * bumpiness)

def best_move(grid, current_tetromino):
    best_evaluation = float('-inf')
    best_x, best_rotation = 0, 0
    
    for rotation in range(len(current_tetromino)):
        for x in range(GRID_WIDTH - len(current_tetromino[0]) + 1):  # Ensure the tetromino fits within grid width
            if is_valid_move(current_tetromino[rotation], x, 0):  # Check for valid starting position
                current_evaluation = evaluate_move(grid, current_tetromino[rotation], x, rotation)
                if current_evaluation > best_evaluation:
                    best_evaluation = current_evaluation
                    best_x, best_rotation = x, rotation
                    
    return best_x, best_rotation