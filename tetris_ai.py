from tetris_pieces import tetrominoes, generate_bag
from tetris_constants import ACTIONS, GRID_WIDTH
from tetris_grid import is_valid_move, place_tetromino_on_grid

def compute_reward(old_state, new_state, game_over):
    reward = 0

    # Reshape the flattened grid into a 2D list
    old_grid_2d = [old_state['grid'][i:i+GRID_WIDTH] for i in range(0, len(old_state['grid']), GRID_WIDTH)]
    new_grid_2d = [new_state['grid'][i:i+GRID_WIDTH] for i in range(0, len(new_state['grid']), GRID_WIDTH)]

    # Calculate line clears
    old_clears = sum(1 for row in old_grid_2d if all(row))
    new_clears = sum(1 for row in new_grid_2d if all(row))
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
    # Reshape the flattened grid into a 2D matrix
    grid_2d = [new_state['grid'][i:i+GRID_WIDTH] for i in range(0, len(new_state['grid']), GRID_WIDTH)]

    holes = sum(1 for x in range(len(grid_2d[0])) 
                for y in range(len(grid_2d)-1) 
                if grid_2d[y][x] and not grid_2d[y+1][x])
    reward -= 5 * holes


    # Penalize height
    max_height = max((y for y in range(len(grid_2d)) if any(grid_2d[y])), default=0) #default if no blocks placed
    reward -= max_height

    # Game over penalty
    if game_over:
        reward -= 500

    return reward


def generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino):    # 1. Grid State:
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
