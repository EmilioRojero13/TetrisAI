import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 10
LOCK_DELAY = 1

GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
BORDER_THICKNESS = 3

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
COLORS = {
    "O": (255, 255, 0),
    "I": (0, 255, 255),
    "S": (0, 255, 0),
    "Z": (255, 0, 0),
    "L": (255, 165, 0),
    "J": (0, 0, 255),
    "T": (128, 0, 128),
}

# Tetris Pieces
PIECES = {
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "S": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "Z": [(1, 0), (0, 0), (0, 1), (-1, 1)],
    "L": [(-1, 0), (0, 0), (1, 0), (1, 1)],
    "J": [(-1, 0), (0, 0), (1, 0), (-1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
}

# Board positioning
BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
PADDING = 40

PLAYER_X = (WIDTH // 2) - BOARD_WIDTH - (PADDING // 2)
AI_X = (WIDTH // 2) + (PADDING // 2)
BOARD_Y = (HEIGHT // 2) - (BOARD_HEIGHT // 2)

# Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris AI vs Human")

clock = pygame.time.Clock()

# Grids
player_grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Draw the game board
def draw_board(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BOARD_WIDTH, BOARD_HEIGHT), BORDER_THICKNESS)
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(x + col * CELL_SIZE, y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

# Draw pieces
def draw_piece(x, y, shape, color):
    for dx, dy in shape:
        rect = pygame.Rect(x + (dx * CELL_SIZE), y + (dy * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

# Check if a move is valid
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

# Rotate a piece
def rotate_piece(shape):
    return [(dy, -dx) for dx, dy in shape]

# Clear completed lines
def clear_lines(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    new_grid = [[None] * GRID_WIDTH for _ in range(lines_cleared)] + new_grid
    return new_grid, lines_cleared

# Display game message
def display_message(text, color):
    font = pygame.font.Font(None, 74)
    message = font.render(text, True, color)
    message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(message, message_rect)

# Generate a new piece
def new_piece():
    piece_type = random.choice(list(PIECES.keys()))
    return PIECES[piece_type], piece_type, COLORS[piece_type]

# Game state variables
current_piece, current_type, piece_color = new_piece()
current_x, current_y = GRID_WIDTH // 2, 0

lock_timer = None
running = True
game_over = False
last_movement_time = 0
rotation_pressed = False  

# Main Game Loop
while running:
    screen.fill(BLACK)

    # Handle game over
    if game_over:
        display_message("You Win!", COLORS["S"])
        pygame.display.flip()
        pygame.time.delay(2000)
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:  
            if event.key == pygame.K_UP and not rotation_pressed:  
                rotated_piece = rotate_piece(current_piece)
                if valid_move(rotated_piece, (current_x, current_y), player_grid):
                    current_piece = rotated_piece
                rotation_pressed = True  

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                rotation_pressed = False  

    keys = pygame.key.get_pressed()
    moved = False

    # Continuous movement with key hold
    if keys[pygame.K_LEFT]:
        if valid_move(current_piece, (current_x - 1, current_y), player_grid):
            current_x -= 1
            moved = True
    if keys[pygame.K_RIGHT]:
        if valid_move(current_piece, (current_x + 1, current_y), player_grid):
            current_x += 1
            moved = True
    if keys[pygame.K_DOWN]:
        if valid_move(current_piece, (current_x, current_y + 1), player_grid):
            current_y += 1
            moved = True

    # Apply gravity
    if pygame.time.get_ticks() - last_movement_time > 1000 // FPS:
        if valid_move(current_piece, (current_x, current_y + 1), player_grid):
            current_y += 1
            lock_timer = None
        else:
            if lock_timer is None:
                lock_timer = time.time()
            elif time.time() - lock_timer >= LOCK_DELAY:
                for dx, dy in current_piece:
                    player_grid[current_y + dy][current_x + dx] = piece_color
                if current_y < 1:
                    game_over = True
                player_grid, _ = clear_lines(player_grid)
                current_piece, current_type, piece_color = new_piece()
                current_x, current_y = GRID_WIDTH // 2, 0
                lock_timer = None
        last_movement_time = pygame.time.get_ticks()

    # Draw player board
    draw_board(PLAYER_X, BOARD_Y)

    # Draw player grid
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if player_grid[row][col] is not None:
                draw_piece(PLAYER_X + col * CELL_SIZE, BOARD_Y + row * CELL_SIZE, [(0, 0)], player_grid[row][col])

    # Draw current piece
    draw_piece(PLAYER_X + current_x * CELL_SIZE, BOARD_Y + current_y * CELL_SIZE, current_piece, piece_color)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
