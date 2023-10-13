# tetris_grid.py

# Grid Dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Initialize the grid with all zeros (empty cells)
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def is_valid_move(tetromino, x, y, rotation=None):
    if rotation is not None:
        tetromino = tetromino[rotation]
    
    for block in tetromino:
        # Check boundaries
        if x + block[0] < 0 or x + block[0] >= GRID_WIDTH:
            return False
        if y + block[1] < 0 or y + block[1] >= GRID_HEIGHT:
            return False
        
        # Check grid collision
        if grid[y + block[1]][x + block[0]] != 0:
            return False
    return True

def place_tetromino_on_grid(tetromino, x, y, tetromino_id):
    for block in tetromino:
        grid_x = x + block[0]
        grid_y = y + block[1]
        
        # Check if the grid coordinates are within bounds
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            grid[grid_y][grid_x] = tetromino_id


def clear_complete_lines():
    global grid
    lines_to_clear = [i for i, line in enumerate(grid) if all(cell != 0 for cell in line)]
    
    # For each cleared line, move everything above it down by one row
    for line in lines_to_clear:
        grid.pop(line)
        grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    
    return len(lines_to_clear)
