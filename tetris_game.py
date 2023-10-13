import pygame
import random
from tetris_grid import GRID_WIDTH, GRID_HEIGHT, grid, is_valid_move, place_tetromino_on_grid, clear_complete_lines
from tetris_pieces import tetrominoes

# Initialization
pygame.init()

# Constants
PADDING = 50
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 2 * PADDING + (10 * CELL_SIZE)
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + PADDING


WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]

# Font
FONT_SIZE = 30
font = pygame.font.Font(None, FONT_SIZE)  # Use the default Pygame font

# Create the screen and clock objects
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def generate_bag():
    return random.sample(tetrominoes, len(tetrominoes))

def draw_tetromino(tetromino, x, y, color):
    for block in tetromino:
        pygame.draw.rect(screen, color, ((x + block[0]) * CELL_SIZE + PADDING, (y + block[1]) * CELL_SIZE + PADDING, CELL_SIZE, CELL_SIZE))

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 0:
                color = COLORS[grid[y][x] - 1]
                pygame.draw.rect(screen, color, (x * CELL_SIZE + PADDING, y * CELL_SIZE + PADDING, CELL_SIZE, CELL_SIZE))

def draw_grid_background():
    for y in range(GRID_HEIGHT + 1):  # +1 to ensure we draw the bottom-most horizontal line
        pygame.draw.line(screen, (200, 200, 200), (PADDING, y * CELL_SIZE + PADDING), (GRID_WIDTH * CELL_SIZE + PADDING, y * CELL_SIZE + PADDING))

    for x in range(GRID_WIDTH + 1):  # +1 to ensure we draw the right-most vertical line
        pygame.draw.line(screen, (200, 200, 200), (x * CELL_SIZE + PADDING, PADDING), (x * CELL_SIZE + PADDING, GRID_HEIGHT * CELL_SIZE + PADDING))

def drop_tetromino(tetromino, x, y):
    drop_distance = 0
    while is_valid_move(tetromino, x, y + 1):
        y += 1
        drop_distance += 1
    # Find the base tetromino that matches the current one
    matching_tetromino = next((t for t in tetrominoes if tetromino in t), None)

    if matching_tetromino is not None:
        place_tetromino_on_grid(tetromino, x, y, tetrominoes.index(matching_tetromino) + 1)
    
    return GRID_WIDTH // 2, 0, drop_distance

def draw_held_tetromino_box(tetromino):
    if not tetromino:  # If there's no held tetromino, just return
        return

    box_start_x = GRID_WIDTH * CELL_SIZE + 2 * PADDING
    box_start_y = PADDING
    box_width = 4 * CELL_SIZE  # Adjust these values to control the size of the box
    box_height = 4 * CELL_SIZE

    pygame.draw.rect(screen, (0, 0, 0), (box_start_x, box_start_y, box_width, box_height), 2)  # Draw the box

    # Compute offsets to center the tetromino in the box
    tetromino_width = max(block[0] for block in tetromino[0]) - min(block[0] for block in tetromino[0]) + 1
    tetromino_height = max(block[1] for block in tetromino[0]) - min(block[1] for block in tetromino[0]) + 1
    offset_x = (4 - tetromino_width) / 2
    offset_y = (4 - tetromino_height) / 2

    for block in tetromino[0]:  # We'll use the default rotation for display
        color = COLORS[tetrominoes.index(tetromino) % len(COLORS)]
        pygame.draw.rect(screen, color, ((box_start_x + (block[0] + offset_x) * CELL_SIZE), (box_start_y + (block[1] + offset_y) * CELL_SIZE), CELL_SIZE, CELL_SIZE))



def main():
    running = True
    bag = generate_bag()
    current_tetromino = bag.pop()
    next_tetromino = bag.pop()
    held_tetromino = None
    current_rotation = 0
    tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
    score = 0
    fall_delay = 500
    fall_timer = pygame.time.get_ticks()
    switched_this_drop = False
    level = 0
    lines_cleared_total = 0

    while running:
        screen.fill(WHITE)
        draw_grid_background()
        # Quit and Keyboard Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if is_valid_move(current_tetromino[current_rotation], tetromino_x - 1, tetromino_y):
                        tetromino_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if is_valid_move(current_tetromino[current_rotation], tetromino_x + 1, tetromino_y):
                        tetromino_x += 1
                elif event.key == pygame.K_DOWN:
                    fall_delay = 50
                elif event.key == pygame.K_UP:
                    next_rotation = (current_rotation + 1) % len(current_tetromino)
                    if is_valid_move(current_tetromino[next_rotation], tetromino_x, tetromino_y):
                        current_rotation = next_rotation
                elif event.key == pygame.K_c:
                    if not switched_this_drop:
                        if not held_tetromino:
                            held_tetromino, current_tetromino = current_tetromino, next_tetromino
                            if not bag:
                                bag = generate_bag()
                            next_tetromino = bag.pop()
                        else:
                            held_tetromino, current_tetromino = current_tetromino, held_tetromino
                        current_rotation = 0
                        tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
                        switched_this_drop = True
                elif event.key == pygame.K_SPACE:
                    drop_dist = 0
                    tetromino_x, tetromino_y, drop_dist = drop_tetromino(current_tetromino[current_rotation], tetromino_x, tetromino_y)
                    switched_this_drop = False
                    current_tetromino = next_tetromino
                    if not bag:
                        bag = generate_bag()
                    next_tetromino = bag.pop()
                    score += drop_dist * 2

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fall_delay = 500

        current_time = pygame.time.get_ticks()
        # Piece falling logic
        if current_time - fall_timer > fall_delay:
            fall_timer = current_time
            if is_valid_move(current_tetromino[current_rotation], tetromino_x, tetromino_y + 1):
                tetromino_y += 1
                if(fall_delay == 50):
                    score += 1
            else:
                place_tetromino_on_grid(current_tetromino[current_rotation], tetromino_x, tetromino_y, tetrominoes.index(current_tetromino) + 1)
                current_tetromino = next_tetromino
                switched_this_drop = False
                if not bag:
                    bag = generate_bag()
                next_tetromino = bag.pop()
                current_rotation = 0
                tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
                if not is_valid_move(current_tetromino[current_rotation], tetromino_x, tetromino_y):
                    running = False

        lines_cleared = clear_complete_lines()
        lines_cleared_total += lines_cleared  # Keep track of total lines cleared

        # Score logic
        if lines_cleared == 1:
            score += (40 * (level + 1))
        elif lines_cleared == 2:
            score += (100 * (level + 1))
        elif lines_cleared == 3:
            score += (300 * (level + 1))
        elif lines_cleared == 4:
            score += (1200 * (level + 1))

        # Increase level every ten lines
        #if lines_cleared_total >= 10:
            #level += 1
            #lines_cleared_total -= 10  # Reset the counter for the next level

        draw_tetromino(current_tetromino[current_rotation], tetromino_x, tetromino_y, COLORS[tetrominoes.index(current_tetromino) % len(COLORS)])
        draw_grid()
        draw_held_tetromino_box(held_tetromino)

        score_text = font.render(f'Score: {score}', True, (0, 0, 0))  # Render the score with black color
        score_pos = (SCREEN_WIDTH - score_text.get_width() - 10, 10)  # Position to display at top right, 10 pixels from the edge
        screen.blit(score_text, score_pos)  # Draw the rendered score on the screen

        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
