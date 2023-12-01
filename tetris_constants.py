import pygame

# Initialization
pygame.init()

# Constants
PADDING = 50
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 2 * PADDING + (10 * CELL_SIZE)
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + PADDING
BATCH_SIZE = 128

NUM_TETROMINO_TYPES = 7

# TODO: Increase batch size?

WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]

# Font
FONT_SIZE = 30
font = pygame.font.Font('./Utils/Font/Helvetica.ttf', FONT_SIZE)

# Define a set of actions
MOVE_ACTIONS = ['LEFT', 'RIGHT', 'HARD_DROP', 'HOLD']
ROTATIONS = [0, 1, 2, 3]  # Assuming max 4 rotations as usual for Tetris pieces

ACTIONS = [(move, rot) for move in MOVE_ACTIONS for rot in ROTATIONS]
