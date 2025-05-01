from board import Board
from piece import PIECES, COLORS, ROTATION_LIMITS, Piece
from collections import deque

# Heuristic Evaluation Function
def evaluate_board(grid):
    holes = 0
    height = 0
    full_lines = 0
    bumpiness = 0
    column_heights = [0] * len(grid[0])

    # Count holes, height, and full lines
    for x in range(len(grid[0])):  # Iterate over columns
        hole_in_column = False
        for y in range(len(grid)):  # Iterate over rows
            if grid[y][x] is not None:
                if column_heights[x] == 0:
                    column_heights[x] = len(grid) - y  # Height of the column
                if hole_in_column:
                    holes += 1  # Count holes beneath filled cells
            else:
                hole_in_column = True

    # Calculate bumpiness (difference in column heights)
    for i in range(len(column_heights) - 1):
        bumpiness += abs(column_heights[i] - column_heights[i + 1])

    # Count full lines
    for row in grid:
        if all(cell is not None for cell in row):
            full_lines += 1

    # Weighted score prioritizing line clears heavily
    return (
        -0.5 * height     # Slightly penalize height
        - 1.5 * holes      # Heavily penalize holes
        - 0.5 * bumpiness  # Penalize bumpy boards
        + 1000 * full_lines  # Strongly reward clearing lines
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


def rotate_piece(shape):
    return [(dy, -dx) for dx, dy in shape]

def ai_move(ai_x, ai_y, ai_piece, ai_color, ai_grid, ai_piece_queue, user_piece_queue):
    # Simulate possible moves and rotations
    best_move = None
    best_evaluation = float('-inf')  # We want to maximize the score

    for rotation in range(4):  # Try all 4 rotations
        rotated_piece = rotate_piece(ai_piece)
        
        for x_offset in range(-5, 6):  # Try horizontal movement within a range
            temp_x = ai_x + x_offset
            temp_y = ai_y

            # Check if the rotated piece can fit at the new position
            if valid_move(rotated_piece, (temp_x, temp_y), ai_grid):
                # Let the piece fall to the bottom of the board
                while valid_move(rotated_piece, (temp_x, temp_y + 1), ai_grid):
                    temp_y += 1

                # Evaluate the position
                temp_grid = [row[:] for row in ai_grid]  # Make a copy of the AI grid
                for px, py in rotated_piece:
                    if 0 <= temp_y + py < len(temp_grid) and 0 <= temp_x + px < len(temp_grid[0]):
                        temp_grid[temp_y + py][temp_x + px] = ai_color

                # Use the heuristic to evaluate the board state after this move
                evaluation = evaluate_board(temp_grid)

                # If the evaluation is better than the current best, update
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    best_move = (temp_x, temp_y, rotated_piece)

    if best_move:
        ai_x, ai_y, ai_piece = best_move
    return ai_x, ai_y, ai_piece
