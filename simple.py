from board import Board
from piece import PIECES, COLORS, ROTATION_LIMITS, Piece
from collections import deque
def rotate_piece(shape):
    return [(dy, -dx) for dx, dy in shape]

def apply_rotation(shape, times):
    rotated = shape
    for _ in range(times):
        rotated = rotate_piece(rotated)
    return rotated

def evaluate_board(grid):
    holes = 0
    full_lines = 0
    bumpiness = 0
    aggregate_height = 0
    column_heights = [0] * len(grid[0])

    for x in range(len(grid[0])):
        block_found = False
        for y in range(len(grid)):
            if grid[y][x] is not None:
                if not block_found:
                    column_heights[x] = len(grid) - y
                    block_found = True
            elif block_found:
                holes += 1

    aggregate_height = sum(column_heights)

    for i in range(len(column_heights) - 1):
        bumpiness += abs(column_heights[i] - column_heights[i + 1])

    for row in grid:
        if all(cell is not None for cell in row):
            full_lines += 1

    return (
        -0.51066 * aggregate_height
        - 0.35663 * holes
        - 0.184483 * bumpiness
        + 0.760666 * full_lines
    )

def valid_move(shape, offset, grid):
    off_x, off_y = offset
    for dx, dy in shape:
        x = off_x + dx
        y = off_y + dy
        if x < 0 or x >= 10 or y >= 20:
            return False  
        if y >= 0 and grid[y][x] is not None:
            return False  
    return True

def ai_move(ai_x, ai_y, ai_piece, ai_color, ai_grid, ai_piece_queue, user_piece_queue):
    best_move = None
    best_evaluation = float('-inf')

    for rot in range(4):
        rotated_piece = apply_rotation(ai_piece, rot)

        for x in range(0, len(ai_grid[0])):
            temp_x = x
            temp_y = ai_y

            # Check initial validity
            if not valid_move(rotated_piece, (temp_x, temp_y), ai_grid):
                continue

            # Let the piece fall to the bottom
            while valid_move(rotated_piece, (temp_x, temp_y + 1), ai_grid):
                temp_y += 1

            # Simulate grid after placing piece
            temp_grid = [row[:] for row in ai_grid]
            for px, py in rotated_piece:
                x_pos = temp_x + px
                y_pos = temp_y + py
                if 0 <= y_pos < len(temp_grid) and 0 <= x_pos < len(temp_grid[0]):
                    temp_grid[y_pos][x_pos] = ai_color

            evaluation = evaluate_board(temp_grid)

            if evaluation > best_evaluation:
                best_evaluation = evaluation
                best_move = (temp_x, temp_y, rotated_piece, rot)

    if best_move:
        return best_move[:3]  # Return x, y, rotated_shape (can add rot if needed)
    else:
        return ai_x, ai_y, ai_piece  # fallback
