# L Tetromino
L_SHAPE = [
    [(2, 0), (0, 1), (1, 1), (2, 1)],
    [(1, 0), (1, 1), (1, 2), (2, 2)],  # Corrected fourth rotation
    [(0, 1), (1, 1), (2, 1), (0, 2)],
    [(0, 0), (1, 0), (1, 1), (1, 2)]
]

# J Tetromino
J_SHAPE = [
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(1, 0), (2, 0), (1, 1), (1, 2)],
    [(0, 1), (1, 1), (2, 1), (2, 2)],
    [(1, 0), (1, 1), (1, 2), (0, 2)]
]

# T Tetromino
T_SHAPE = [
    [(1, 0), (0, 1), (1, 1), (2, 1)],
    [(1, 0), (1, 1), (1, 2), (2, 1)],
    [(0, 1), (1, 1), (2, 1), (1, 2)],
    [(1, 0), (0, 1), (1, 1), (1, 2)]
]

# O Tetromino
O_SHAPE = [
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)]
]

# I Tetromino
I_SHAPE = [
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)]
]

# S Tetromino
S_SHAPE = [
    [(1, 0), (2, 0), (0, 1), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)],
    [(1, 0), (2, 0), (0, 1), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)]
]

# Z Tetromino
Z_SHAPE = [
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(2, 0), (1, 1), (2, 1), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(2, 0), (1, 1), (2, 1), (1, 2)]
]


tetrominoes = [O_SHAPE, I_SHAPE, T_SHAPE, S_SHAPE, Z_SHAPE, J_SHAPE, L_SHAPE]
