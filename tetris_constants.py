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

WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]

# Font
FONT_SIZE = 30
font = pygame.font.Font('./Utils/Font/Helvetica.ttf', FONT_SIZE)

# Create the screen and clock objects
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
