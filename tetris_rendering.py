import pygame
from tetris_constants import CELL_SIZE, COLORS, screen, font, PADDING, GRID_HEIGHT, GRID_WIDTH, FONT_SIZE
from tetris_pieces import tetrominoes
from tetris_grid import grid

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

def draw_held_tetromino_box(tetromino):
    box_start_x = GRID_WIDTH * CELL_SIZE + 2 * PADDING
    box_start_y = PADDING
    box_width = 4 * CELL_SIZE  # Adjust these values to control the size of the box
    box_height = 4 * CELL_SIZE

    pygame.draw.rect(screen, (0, 0, 0), (box_start_x, box_start_y, box_width, box_height), 2)  # Always draw the box
    draw_box_label(box_start_x, box_start_y - FONT_SIZE - 10, box_width, "Held")

    if not tetromino:  # If there's no held tetromino, just return after drawing the empty box
        return

    # Compute offsets to center the tetromino in the box
    tetromino_width = max(block[0] for block in tetromino[0]) - min(block[0] for block in tetromino[0]) + 1
    tetromino_height = max(block[1] for block in tetromino[0]) - min(block[1] for block in tetromino[0]) + 1
    offset_x = (4 - tetromino_width) / 2
    offset_y = (4 - tetromino_height) / 2

    for block in tetromino[0]:  # We'll use the default rotation for display
        color = COLORS[tetrominoes.index(tetromino) % len(COLORS)]
        pygame.draw.rect(screen, color, ((box_start_x + (block[0] + offset_x) * CELL_SIZE), (box_start_y + (block[1] + offset_y) * CELL_SIZE), CELL_SIZE, CELL_SIZE))


def draw_next_tetromino_box(tetromino):
    if not tetromino:  # If there's no next tetromino, just return
        return

    box_start_x = GRID_WIDTH * CELL_SIZE + 2 * PADDING
    box_start_y = 2 * PADDING + 4 * CELL_SIZE  # Below the held tetromino box
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
        draw_box_label(box_start_x, box_start_y - FONT_SIZE - 10, box_width, "Next")
        pygame.draw.rect(screen, color, ((box_start_x + (block[0] + offset_x) * CELL_SIZE), (box_start_y + (block[1] + offset_y) * CELL_SIZE), CELL_SIZE, CELL_SIZE))

def draw_box_label(x, y, box_width, text):
    label = font.render(text, True, (0, 0, 0))  # Render the label with black color
    label_width = label.get_width()
    centered_x = x + (box_width - label_width) / 2  # Centering the label
    screen.blit(label, (centered_x, y))  # Draw the rendered text on the screen