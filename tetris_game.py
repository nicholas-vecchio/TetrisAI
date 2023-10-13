import pygame
import random
from tetris_grid import GRID_WIDTH, GRID_HEIGHT, grid, is_valid_move, place_tetromino_on_grid, clear_complete_lines
from tetris_pieces import tetrominoes

# Initialization
pygame.init()

# Constants
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]

# Create the screen and clock objects
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def generate_bag():
    return random.sample(tetrominoes, len(tetrominoes))

def draw_tetromino(tetromino, x, y, color):
    for block in tetromino:
        pygame.draw.rect(screen, color, ((x + block[0]) * CELL_SIZE, (y + block[1]) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 0:
                color = COLORS[grid[y][x] - 1]
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

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

    while running:
        screen.fill(WHITE)

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

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fall_delay = 500

        current_time = pygame.time.get_ticks()
        if current_time - fall_timer > fall_delay:
            fall_timer = current_time
            if is_valid_move(current_tetromino[current_rotation], tetromino_x, tetromino_y + 1):
                tetromino_y += 1
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
        if lines_cleared:
            score += lines_cleared * 10

        draw_tetromino(current_tetromino[current_rotation], tetromino_x, tetromino_y, COLORS[tetrominoes.index(current_tetromino) % len(COLORS)])
        draw_grid()
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
