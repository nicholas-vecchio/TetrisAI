from tetris_pieces import tetrominoes, generate_bag
from tetris_constants import ACTIONS, GRID_WIDTH
from tetris_grid import is_valid_move, place_tetromino_on_grid

def compute_reward(old_state, new_state, game_over):
    reward = 0

    # Reward for placing a piece
    reward += 1

    # Calculate line clears
    old_clears = sum(1 for row in old_state['grid'] if all(row))
    new_clears = sum(1 for row in new_state['grid'] if all(row))
    line_clears = new_clears - old_clears

    if line_clears == 1:
        reward += 10
    elif line_clears == 2:
        reward += 30
    elif line_clears == 3:
        reward += 60
    elif line_clears == 4:
        reward += 100

    # Penalize holes
    holes = sum(1 for x in range(len(new_state['grid'][0])) 
                for y in range(len(new_state['grid'])-1) 
                if new_state['grid'][y][x] and not new_state['grid'][y+1][x])
    reward -= 5 * holes

    # Penalize height
    max_height = max(y for y in range(len(new_state['grid'])) if any(new_state['grid'][y]))
    reward -= max_height

    # Game over penalty
    if game_over:
        reward -= 500

    return reward


def generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino=None):    # 1. Grid State:
    grid_state = [cell for row in grid for cell in row]

    # 2. Current Tetromino State:
    tetromino_type = tetrominoes.index(current_tetromino)
    tetromino_position = (tetromino_x, tetromino_y)
    tetromino_rotation = current_rotation

    # 3. Next Tetromino State:
    next_tetromino_type = tetrominoes.index(next_tetromino)

    # Combine into a single state dictionary
    state = {
        "grid": grid_state,
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

    # Handle different move actions
    if move == 'LEFT':
        if is_valid_move(rotated_tetromino, new_state['tetromino_position'][0] - 1, new_state['tetromino_position'][1]):
            new_state['tetromino_position'] = (new_state['tetromino_position'][0] - 1, new_state['tetromino_position'][1])
    
    elif move == 'RIGHT':
        if is_valid_move(rotated_tetromino, new_state['tetromino_position'][0] + 1, new_state['tetromino_position'][1]):
            new_state['tetromino_position'] = (new_state['tetromino_position'][0] + 1, new_state['tetromino_position'][1])
    
    elif move == 'SOFT_DROP':
        if is_valid_move(rotated_tetromino, new_state['tetromino_position'][0], new_state['tetromino_position'][1] + 1):
            new_state['tetromino_position'] = (new_state['tetromino_position'][0], new_state['tetromino_position'][1] + 1)

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
            new_state["has_held"] = True 

    new_state['tetromino_rotation'] = rotation

    # Return the new state
    return new_state
