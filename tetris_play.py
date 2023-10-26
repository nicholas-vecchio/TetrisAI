from tetris_constants import SCREEN_HEIGHT, SCREEN_WIDTH, COLORS, WHITE, GRID_HEIGHT, GRID_WIDTH
from tetris_grid import reset_grid, grid
from tetris_rendering import draw_grid, draw_grid_background, draw_held_tetromino_box, draw_next_tetromino_box, draw_tetromino
from tetris_pieces import generate_bag, tetrominoes
from tetris_ai import generate_state, apply_action
from DQN import DQNAgent
import pygame
import sys

def visualize_play(agent):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris AI Visualization")

    running = True
    bag = generate_bag()
    current_tetromino = bag.pop()
    next_tetromino = bag.pop()
    held_tetromino = None
    current_rotation = 0
    tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
    has_held = False
    reset_grid()

    while running:
        screen.fill(WHITE)
        draw_grid_background()

        # AI Decision Making
        state = generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino)
        action = agent.act(state)
        move, rotation = action

        new_state = apply_action(current_tetromino, action, state, next_tetromino, bag)
        has_held = new_state["has_held"]
        current_tetromino, tetromino_x, tetromino_y, current_rotation, held_tetromino = new_state['tetromino'], new_state['tetromino_position'][0], new_state['tetromino_position'][1], new_state['tetromino_rotation'], new_state['held_tetromino']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_tetromino(current_tetromino[current_rotation], tetromino_x, tetromino_y, COLORS[tetrominoes.index(current_tetromino) % len(COLORS)])
        draw_grid()
        draw_held_tetromino_box(held_tetromino)
        draw_next_tetromino_box(next_tetromino)

        pygame.display.flip()
        pygame.time.delay(1000)  # Delay to slow down the game for better visualization

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    agent = DQNAgent()
    visualize_play(agent)
