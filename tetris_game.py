import pygame
import random
from tetris_constants import screen, WHITE, COLORS, font, SCREEN_WIDTH, clock, ACTIONS
from tetris_rendering import draw_grid, draw_grid_background, draw_held_tetromino_box, draw_next_tetromino_box, draw_tetromino
from tetris_grid import GRID_WIDTH, is_valid_move, place_tetromino_on_grid, clear_complete_lines, grid
from tetris_pieces import tetrominoes, generate_bag
from DQN import DQNAgent
from tetris_ai import generate_state, apply_action, compute_reward

# TODO: Implement multiple episodes/runs before closing
# TODO: Implement actual training
# TODO: Implement ability to toggle visuals
# TODO: Add reward on screen
# TODO: Add reward into code.
def main():
    pygame.init()
    running = True
    agent = DQNAgent()
    bag = generate_bag()
    current_tetromino = bag.pop()
    next_tetromino = bag.pop()
    held_tetromino = None
    current_rotation = 0
    tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
    score = 0
    fall_delay = 500
    fall_timer = pygame.time.get_ticks()
    level = 0
    lines_cleared_total = 0
    has_held = False

    while running:
        screen.fill(WHITE)
        draw_grid_background()

        # AI Decision Making
        state = generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held)
        
        valid_action = None
        attempts = 0
        while valid_action is None and attempts < 10:
            action = agent.act(state)
            move, rotation = action
            rotated_tetromino = current_tetromino[rotation]
            if is_valid_move(rotated_tetromino, tetromino_x, tetromino_y):
                valid_action = action
            attempts += 1

        action = valid_action if valid_action else random.choice(ACTIONS)  # Use a random action if no valid action is found
        new_state = apply_action(current_tetromino, action, state, next_tetromino, bag)
        has_held = new_state["has_held"]
        print("AI Decision:", action)
        print("Resulting State:", new_state)
        tetromino_x, tetromino_y, current_rotation = new_state['tetromino_position'][0], new_state['tetromino_position'][1], new_state['tetromino_rotation']
        print("Tetromino Position:", tetromino_x, tetromino_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()
        if current_time - fall_timer > fall_delay:
            fall_timer = current_time
            if is_valid_move(current_tetromino, tetromino_x, tetromino_y + 1, current_rotation):
                tetromino_y += 1
                print("Tetromino Moved Down To:", tetromino_y)
                if(fall_delay == 50):
                    score += 1
            else:
                place_tetromino_on_grid(current_tetromino[current_rotation], tetromino_x, tetromino_y, tetrominoes.index(current_tetromino) + 1)
                has_held = False
                print("Placed Tetromino at Position:", tetromino_x, tetromino_y, "Rotation:", current_rotation)
                current_tetromino = next_tetromino
                if not bag:
                    bag = generate_bag()
                next_tetromino = bag.pop()
                current_rotation = 0
                tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
                if not is_valid_move(current_tetromino, tetromino_x, tetromino_y, current_rotation):
                    running = False

        lines_cleared = clear_complete_lines()
        lines_cleared_total += lines_cleared

        if lines_cleared == 1:
            score += (40 * (level + 1))
        elif lines_cleared == 2:
            score += (100 * (level + 1))
        elif lines_cleared == 3:
            score += (300 * (level + 1))
        elif lines_cleared == 4:
            score += (1200 * (level + 1))

        draw_tetromino(current_tetromino[current_rotation], tetromino_x, tetromino_y, COLORS[tetrominoes.index(current_tetromino) % len(COLORS)])
        draw_grid()
        draw_held_tetromino_box(held_tetromino)
        draw_next_tetromino_box(next_tetromino)

        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        score_pos = (SCREEN_WIDTH - score_text.get_width() - 10, 10)
        screen.blit(score_text, score_pos)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)