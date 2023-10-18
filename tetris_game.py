import pygame
import random
import torch
from tetris_constants import SHOW_VISUALS, screen, WHITE, COLORS, font, SCREEN_WIDTH, clock, ACTIONS, GRID_HEIGHT
from tetris_rendering import draw_grid, draw_grid_background, draw_held_tetromino_box, draw_next_tetromino_box, draw_tetromino
from tetris_grid import GRID_WIDTH, is_valid_move, place_tetromino_on_grid, clear_complete_lines, reset_grid, grid
from tetris_pieces import tetrominoes, generate_bag
from DQN import DQNAgent
from tetris_ai import generate_state, apply_action, compute_reward
from concurrent.futures import ProcessPoolExecutor
import copy
from multiprocessing import Manager

# TODO: Fix bug where out of map tetromino doesnt end game
# TODO: add scoring for hard drops/soft drops too maybe
# TODO: Re-add soft drop
# TODO: Parralelism?

def main(agent):
    if(SHOW_VISUALS):
        pygame.init()
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
    level = 0
    lines_cleared_total = 0
    has_held = False
    reset_grid()

    while running:
        if SHOW_VISUALS:
            screen.fill(WHITE)
            draw_grid_background()

        # AI Decision Making
        state = generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino)
        valid_action = None
        attempts = 0
        while valid_action is None and attempts < 10:
            action = agent.act(state)
            move, rotation = action
            rotated_tetromino = current_tetromino[rotation]
            if is_valid_move(rotated_tetromino, tetromino_x, tetromino_y):
                valid_action = action
            attempts += 1

        action = valid_action if valid_action else random.choice(ACTIONS)
        new_state = apply_action(current_tetromino, action, state, next_tetromino, bag)
        has_held = new_state["has_held"]
        current_tetromino, tetromino_x, tetromino_y, current_rotation, held_tetromino = new_state['tetromino'], new_state['tetromino_position'][0], new_state['tetromino_position'][1], new_state['tetromino_rotation'], new_state['held_tetromino']

        if SHOW_VISUALS:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        current_time = pygame.time.get_ticks()
        if current_time - fall_timer > fall_delay:
            fall_timer = current_time
            if is_valid_move(current_tetromino, tetromino_x, tetromino_y + 1, current_rotation):
                tetromino_y += 1
                if(fall_delay == 50):
                    score += 1
            else:
                place_tetromino_on_grid(current_tetromino[current_rotation], tetromino_x, tetromino_y, tetrominoes.index(current_tetromino) + 1)
                has_held = False
                current_tetromino = next_tetromino
                if not bag:
                    bag = generate_bag()
                next_tetromino = bag.pop()
                current_rotation = 0
                tetromino_x, tetromino_y = GRID_WIDTH // 2, 0
                # Check for game over condition when a new tetromino spawns
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

        if SHOW_VISUALS:
            draw_tetromino(current_tetromino[current_rotation], tetromino_x, tetromino_y, COLORS[tetrominoes.index(current_tetromino) % len(COLORS)])
            draw_grid()
            draw_held_tetromino_box(held_tetromino)
            draw_next_tetromino_box(next_tetromino)

        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        score_pos = (SCREEN_WIDTH - score_text.get_width() - 60, 10)

        reward = compute_reward(state, new_state, not running)
        agent.step(state, action, reward, new_state, not running)

        reward_text = font.render(f'Reward: {reward}', True, (0, 0, 0))
        rewards_pos = (SCREEN_WIDTH - score_text.get_width() - 60, 50)
        if(SHOW_VISUALS):
            screen.blit(reward_text, rewards_pos)
            screen.blit(score_text, score_pos)

        if SHOW_VISUALS:
            pygame.display.flip()
            clock.tick(60)

    return score, reward

def episode_wrapper(episode, agent_state_dict, shared_rewards):
    agent = DQNAgent()
    agent.qnetwork.load_state_dict(agent_state_dict)
    
    try:
        score, reward = main(agent)
        print(f"Episode {episode + 1} Score: {score}, Reward: {reward}")
        shared_rewards.append(reward)  # use shared memory to store rewards
        return (score, episode)
    except Exception as e:
        print(f"Error in episode {episode}:", e)
        return None

if __name__ == "__main__":
    agent = DQNAgent()
    num_episodes = 10000
    parallelism = 4  # Number of episodes to run in parallel
    
    manager = Manager()
    shared_rewards = manager.list()  # shared list for rewards
    
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        for i in range(0, num_episodes, parallelism):
            agent_state_dict = agent.qnetwork.state_dict()
            futures = [executor.submit(episode_wrapper, episode=i+j, agent_state_dict=agent_state_dict, shared_rewards=shared_rewards) for j in range(parallelism)]
            
            for future in futures:
                result = future.result()
                if result:
                    score, episode = result
                    if episode % 50 == 0:
                        #agent.plot_rewards(shared_rewards)  # plot using shared_rewards TODO: Fix this
                        torch.save(agent.qnetwork.state_dict(), f"tetris_weights_episode_{episode}.pth")