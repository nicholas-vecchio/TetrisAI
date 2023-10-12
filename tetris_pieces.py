# tetris_pieces.py

# O Tetromino (Square shape)
O_SHAPE = [
    [(0, 0), (1, 0), (0, 1), (1, 1)]  # Only one rotation for the O shape
]

# I Tetromino (Straight line)
I_SHAPE = [
    [(0, 1), (1, 1), (2, 1), (3, 1)],  # Horizontal
    [(2, 0), (2, 1), (2, 2), (2, 3)]   # Vertical
]

# T Tetromino
T_SHAPE = [
    [(1, 0), (0, 1), (1, 1), (2, 1)],
    [(1, 0), (0, 1), (1, 1), (1, 2)],
    [(0, 1), (1, 1), (2, 1), (1, 2)],
    [(1, 0), (1, 1), (2, 1), (1, 2)]
]

# S Tetromino
S_SHAPE = [
    [(1, 0), (2, 0), (0, 1), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)]
]

# Z Tetromino
Z_SHAPE = [
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(1, 0), (0, 1), (1, 1), (0, 2)]
]

# J Tetromino
J_SHAPE = [
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(1, 0), (0, 1), (1, 1), (1, 2)],
    [(0, 1), (1, 1), (2, 1), (2, 2)],
    [(1, 0), (1, 1), (0, 2), (1, 2)]
]

# L Tetromino
L_SHAPE = [
    [(2, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    [(0, 1), (1, 1), (2, 1), (0, 2)],
    [(1, 0), (0, 1), (1, 1), (0, 2)]
]

tetrominoes = [O_SHAPE, I_SHAPE, T_SHAPE, S_SHAPE, Z_SHAPE, J_SHAPE, L_SHAPE]
