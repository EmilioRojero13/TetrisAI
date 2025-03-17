import random
import pygame
from collections import deque
from user import valid_move, rotate_piece, get_next_piece
from pieces import PIECES, COLORS

# AI Falling Speed (in milliseconds)
AI_FALL_SPEED = 200
last_ai_fall_time = pygame.time.get_ticks()

# Heuristic Evaluation Function
def evaluate_board(grid):
    holes = 0
    height = 0
    full_lines = 0
    for x in range(10):
        column_height = 0
        hole_in_column = False
        for y in range(20):
            if grid[y][x] is not None:
                column_height = max(column_height, y)
                if hole_in_column:
                    holes += 1
            else:
                hole_in_column = True
        height += column_height
    return -height - 5 * holes + 100 * full_lines

# AI Decision Making (choose the best move based on the heuristic)
def ai_move(ai_x, ai_y, ai_piece, ai_color, ai_grid, ai_piece_queue, user_piece_queue):
    best_score = float('-inf')
    best_move = None

    for rotation in range(4):  # Try all 4 rotations
        rotated_piece = ai_piece
        for _ in range(rotation):
            rotated_piece = rotate_piece(rotated_piece)

        for dx in range(-10, 10):  # Try all x offsets
            if valid_move(rotated_piece, (ai_x + dx, ai_y), ai_grid):
                # Drop the piece as far as it can go
                y_offset = ai_y
                while valid_move(rotated_piece, (ai_x + dx, y_offset + 1), ai_grid):
                    y_offset += 1

                # Simulate the move
                temp_grid = [row[:] for row in ai_grid]
                for dx, dy in rotated_piece:
                    temp_grid[y_offset + dy][ai_x + dx] = ai_color

                # Evaluate the board state
                score = evaluate_board(temp_grid)

                if score > best_score:
                    best_score = score
                    best_move = (rotation, dx, y_offset)

    if best_move:
        rotation, dx, y_offset = best_move
        for _ in range(rotation):
            ai_piece = rotate_piece(ai_piece)

        ai_x += dx
        ai_y = y_offset

    return ai_x, ai_y, ai_piece
