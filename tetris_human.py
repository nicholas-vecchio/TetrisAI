import pygame
from tetris_constants import COLORS, SCREEN_HEIGHT, SCREEN_WIDTH
from tetris_grid import GRID_WIDTH, is_valid_move, place_tetromino_on_grid, clear_complete_lines, reset_grid, grid
from tetris_pieces import tetrominoes, generate_bag
from tetris_ai import generate_state,  compute_reward
from tetris_rendering import draw_grid, draw_grid_background, draw_next_tetromino_box, draw_held_tetromino_box, draw_tetromino
from multiprocessing import Manager
import matplotlib
matplotlib.use('Agg')
import os
def main():
    clock = pygame.time.Clock()
    running = True
    bag = generate_bag()
    current_tetromino = bag.pop()
    next_tetromino = bag.pop()
    held_tetromino = None
    current_rotation = 0
    tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
    score = 0
    level = 0
    lines_cleared_total = 0
    has_held = False
    cumulative_reward = 0
    num_steps = 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    reset_grid()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # Move left
                    if is_valid_move(current_tetromino, tetromino_x - 1, tetromino_y, current_rotation):
                        tetromino_x -= 1
                elif event.key == pygame.K_RIGHT:
                    # Move right
                    if is_valid_move(current_tetromino, tetromino_x + 1, tetromino_y, current_rotation):
                        tetromino_x += 1
                elif event.key == pygame.K_DOWN:
                    # Soft drop
                    if is_valid_move(current_tetromino, tetromino_x, tetromino_y + 1, current_rotation):
                        tetromino_y += 1
                elif event.key == pygame.K_UP:
                    # Rotate
                    new_rotation = (current_rotation + 1) % len(current_tetromino)
                    if is_valid_move(current_tetromino, tetromino_x, tetromino_y, new_rotation):
                        current_rotation = new_rotation
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while is_valid_move(current_tetromino, tetromino_x, tetromino_y + 1, current_rotation):
                        tetromino_y += 1

        # Check if tetromino should be placed
        if not is_valid_move(current_tetromino, tetromino_x, tetromino_y + 1, current_rotation):
            place_tetromino_on_grid(current_tetromino[current_rotation], tetromino_x, tetromino_y, tetrominoes.index(current_tetromino) + 1)
            current_tetromino = next_tetromino
            if not bag:
                bag = generate_bag()
            next_tetromino = bag.pop()
            current_rotation = 0
            tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
            has_held = False
            if not is_valid_move(current_tetromino, tetromino_x, tetromino_y, current_rotation):
                running = False

        state = generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino)
        lines_cleared = clear_complete_lines()
        lines_cleared_total += lines_cleared
        reward = compute_reward(state, not running, lines_cleared)
        print(reward)
        cumulative_reward += reward
        num_steps += 1

        # Visualization
        screen.fill((255, 255, 255))
        draw_grid_background(screen)
        draw_grid(screen)
        draw_tetromino(screen, current_tetromino[current_rotation], tetromino_x, tetromino_y, COLORS[tetrominoes.index(current_tetromino) % len(COLORS)])
        draw_held_tetromino_box(screen, held_tetromino)
        draw_next_tetromino_box(screen, next_tetromino)
        pygame.display.flip()
        clock.tick(60)

    avg_reward = cumulative_reward / num_steps if num_steps != 0 else 0
    return score, avg_reward, num_steps

# Main Execution
if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()
