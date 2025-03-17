import pygame
import time
from collections import deque
from user import new_piece, get_next_piece, valid_move, rotate_piece, clear_lines ,user_piece_queue
from ai import ai_move, AI_FALL_SPEED, last_ai_fall_time
from pieces import PIECES, COLORS


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 600
FPS = 10
LOCK_DELAY = 1
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
BORDER_THICKNESS = 3

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

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
ai_grid =  [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

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

# Game state variables
current_piece, current_type, piece_color = new_piece()
current_x, current_y = GRID_WIDTH // 2, 0
ai_x, ai_y = current_x, current_y
ai_piece = current_piece
ai_type = current_type
ai_color = piece_color
lock_timer = None
running = True
game_over = False
last_movement_time = 0
rotation_pressed = False 

ai_piece_queue = deque(user_piece_queue)

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

    # Apply gravity to AI with slower speed
    if pygame.time.get_ticks() - last_ai_fall_time > AI_FALL_SPEED:
        if valid_move(ai_piece, (ai_x, ai_y + 1), ai_grid):  
            ai_y += 1
        else:
            # Lock AI piece into place
            for dx, dy in ai_piece:
                ai_grid[ai_y + dy][ai_x + dx] = ai_color

            # Clear full lines
            ai_grid, _ = clear_lines(ai_grid)

            # Spawn a new AI piece at the top
            ai_piece, ai_type, ai_color = get_next_piece("ai", ai_piece_queue, user_piece_queue)

            ai_x, ai_y = GRID_WIDTH // 2, 0

            # Check if the new piece is immediately blocked (AI loses)
            if not valid_move(ai_piece, (ai_x, ai_y), ai_grid):
                print("AI lost!")
                running = False
        last_ai_fall_time = pygame.time.get_ticks()

    # Apply gravity to user
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
                current_piece, current_type, piece_color = get_next_piece("user", ai_piece_queue, user_piece_queue)
                current_x, current_y = GRID_WIDTH // 2, 0
                lock_timer = None
        last_movement_time = pygame.time.get_ticks()

    # Draw player board
    draw_board(PLAYER_X, BOARD_Y)
    draw_board(AI_X, BOARD_Y)

    # Draw player grid
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if player_grid[row][col] is not None:
                draw_piece(PLAYER_X + col * CELL_SIZE, BOARD_Y + row * CELL_SIZE, [(0, 0)], player_grid[row][col])
            if ai_grid[row][col] is not None:
                draw_piece(AI_X + col * CELL_SIZE, BOARD_Y + row * CELL_SIZE, [(0, 0)], ai_grid[row][col])

    # Draw current piece
    draw_piece(PLAYER_X + current_x * CELL_SIZE, BOARD_Y + current_y * CELL_SIZE, current_piece, piece_color)
    draw_piece(AI_X + ai_x * CELL_SIZE, BOARD_Y + ai_y * CELL_SIZE, ai_piece, ai_color)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()