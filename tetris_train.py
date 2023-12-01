import pygame
import random
import torch
from tetris_constants import ACTIONS,  MOVE_ACTIONS, BATCH_SIZE
from tetris_grid import GRID_WIDTH, is_valid_move, place_tetromino_on_grid, clear_complete_lines, reset_grid, grid
from tetris_pieces import tetrominoes, generate_bag
from DQN import DQNAgent
from tetris_ai import generate_state, apply_action, compute_reward
from concurrent.futures import ProcessPoolExecutor
import copy
from multiprocessing import Manager
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from collections import deque

# TODO: add scoring for hard drops/soft drops too maybe
# TODO: Re-add soft drop
# TODO: Profiling
# TODO: Enable use of tensor cores

SAVE_INTERVAL = 50
CHECKPOINT_PATH = "CHECKPOINTS"
MAX_MEM = 100000

def apply_move_action(tetromino, action, x, y, rotation):
    if action == 'LEFT':
        return is_valid_move(tetromino[rotation], x - 1, y)
    elif action == 'RIGHT':
        return is_valid_move(tetromino[rotation], x + 1, y)
    elif action == 'HARD_DROP':
        while is_valid_move(tetromino[rotation], x, y):
            y += 1
        return y > 0
    elif action == 'HOLD':
        return True
    return False

def main(agent, shared_experience):
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
    cumulative_reward = 0
    num_steps = 0
    reset_grid()

    while running:
        # AI Decision Making
        state = generate_state(grid, current_tetromino, tetromino_x, tetromino_y, current_rotation, next_tetromino, has_held, held_tetromino)
        valid_action = None
        attempts = 0

        while valid_action is None and attempts < 10:
            action = agent.act(state)
            move, rotation = action
            if move in MOVE_ACTIONS and apply_move_action(current_tetromino, move, tetromino_x, tetromino_y, rotation):
                valid_action = action
            attempts += 1

        if valid_action:
            action = valid_action
        else:
            valid_actions = [a for a in ACTIONS if apply_move_action(current_tetromino, a[0], tetromino_x, tetromino_y, a[1])]
            action = random.choice(valid_actions)

        move, rotation = action

        new_state = apply_action(current_tetromino, action, state, next_tetromino, bag)
        has_held = new_state["has_held"]
        current_tetromino, tetromino_x, tetromino_y, current_rotation, held_tetromino = new_state['tetromino'], new_state['tetromino_position'][0], new_state['tetromino_position'][1], new_state['tetromino_rotation'], new_state['held_tetromino']

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

        reward = compute_reward(new_state, not running, lines_cleared)
        cumulative_reward += reward
        num_steps += 1
        agent.step(state, action, reward, new_state, not running)
        experience = (state, action, reward, new_state, not running)
        shared_experience.append(experience)

    avg_reward = cumulative_reward/ num_steps if num_steps != 0 else 0

    return score, avg_reward, num_steps

def latest_checkpoint():
    if not os.path.exists(CHECKPOINT_PATH):
        os.makedirs(CHECKPOINT_PATH)

    
    all_checkpoints = [f for f in os.listdir(CHECKPOINT_PATH) if os.path.isfile(os.path.join(CHECKPOINT_PATH, f)) and f.endswith(".pth")]
    if not all_checkpoints:
        return None

    return max(all_checkpoints, key=lambda x: int(x.split('_')[2].split('.')[0]))

def episode_wrapper(agent, episode, shared_rewards, shared_experience):    
    try:
        score, reward, num_steps = main(agent, shared_experience)  # Pass shared experience to main function
        print(f"Episode {episode + 1} Score: {score}, Num Steps: {num_steps}")
        shared_rewards.append(reward)
        return (score, episode)
    except Exception as e:
        print(f"Error in episode {episode}:", e)
        return None

if __name__ == "__main__":
    agent = DQNAgent()

    # Try to load from the latest checkpoint
    checkpoint_filename = latest_checkpoint()
    start_episode = 0
    if checkpoint_filename:
        checkpoint_path = os.path.join(CHECKPOINT_PATH, checkpoint_filename)
        print(checkpoint_filename)
        agent.qnetwork.load_state_dict(torch.load(checkpoint_path))
        start_episode = int(checkpoint_filename.split('_')[2].split('.')[0]) + 1  # extract episode number and increment
        agent.epsilon = max(agent.epsilon_min, agent.epsilon * (agent.epsilon_decay ** start_episode))

    num_episodes = 1000
    parallelism = 4
    window_size = 1000
    
    manager = Manager()
    shared_rewards = manager.list()
    shared_experience = manager.list(deque(maxlen=MAX_MEM))   
    epsilons = []
    batch_size = BATCH_SIZE

    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        for i in range(start_episode, start_episode + num_episodes, parallelism): # Start from the last episode
            agent_state_dict = agent.qnetwork.state_dict()
            futures = [executor.submit(episode_wrapper, agent=agent, episode=i+j, shared_rewards=shared_rewards, shared_experience=shared_experience) for j in range(parallelism)]

            for future in futures:
                result = future.result()
                if result:
                    score, episode = result
                    
                    # Ensure checkpoint directory exists
                    if not os.path.exists(CHECKPOINT_PATH):
                        os.makedirs(CHECKPOINT_PATH)
                    
                    # Save checkpoint
                    if(episode % SAVE_INTERVAL == 0):
                        checkpoint_filename = f"tetris_checkpoint_{episode}.pth"
                        checkpoint_path = os.path.join(CHECKPOINT_PATH, checkpoint_filename)
                        torch.save(agent.qnetwork.state_dict(), checkpoint_path)
                    
                    if len(shared_experience) >= batch_size:
                        batch = random.sample(list(shared_experience), batch_size)
                        for experience in batch:
                            state, action, reward, new_state, done = experience
                            agent.step(state, action, reward, new_state, done)
                    
                    agent.epsilon = max(agent.epsilon_min, agent.epsilon_decay*agent.epsilon)
                    epsilons.append(agent.epsilon)
    end_episode = start_episode+num_episodes
    agent.plot_rewards(end_episode)
    agent.plot_loss(end_episode)
    agent.plot_action_distribution(end_episode)
    agent.plot_episode_length(end_episode)
    agent.plot_epsilon(end_episode)