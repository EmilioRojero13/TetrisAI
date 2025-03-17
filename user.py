import random
from collections import deque
from pieces import PIECES, COLORS

# Constants
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30

def new_piece():
    piece_type = random.choice(list(PIECES.keys()))
    return PIECES[piece_type], piece_type, COLORS[piece_type]

def valid_move(shape, offset, grid):
    off_x, off_y = offset
    for dx, dy in shape:
        x = off_x + dx
        y = off_y + dy
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False  
        if y >= 0 and grid[y][x] is not None:
            return False  
    return True

def rotate_piece(shape):
    return [(dy, -dx) for dx, dy in shape]

# Shared piece queue
user_piece_queue = deque([])
for i in range(5):
    user_piece_queue.append(new_piece())

def get_next_piece(player, ai_piece_queue, user_piece_queue):
    new_addition = new_piece()
    ai_piece_queue.append(new_addition)
    user_piece_queue.append(new_addition)
    if player == "ai":
        return ai_piece_queue.popleft()
    if player == "user":
        return user_piece_queue.popleft()
    
# Clear completed lines
def clear_lines(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    new_grid = [[None] * GRID_WIDTH for _ in range(lines_cleared)] + new_grid
    return new_grid, lines_cleared


