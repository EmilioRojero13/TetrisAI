import pygame
import sys
import threading
from board import Board
from ai import AI
import simple

pygame.init()

WIDTH, HEIGHT = 1500, 750
FPS = 10
BACKGROUND_COLOR = (0, 0, 0)
CELL_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20

USER_BOARD_X, USER_BOARD_Y = 100, 50
AI_BOARD_X, AI_BOARD_Y = 550, 50
SIMPLE_H_X, SIMPLE_H_Y = 1000, 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetrio")

font = pygame.font.SysFont("Arial", 24)
bold_font = pygame.font.SysFont("Arial", 32, bold=True)

clock = pygame.time.Clock()

user_board = Board(GRID_WIDTH, GRID_HEIGHT)
ai_board = Board(GRID_WIDTH, GRID_HEIGHT)
simple_h_board = Board(GRID_WIDTH, GRID_HEIGHT)

fall_time = 0
fall_speed = 170
ai_player = AI()

ai_thread = None
ai_next_move = None
ai_computing = False
ai_move_ready = False

# Timer initialization
user_start_ticks = pygame.time.get_ticks()
ai_start_ticks = pygame.time.get_ticks()
simple_start_ticks = pygame.time.get_ticks()

user_final_runtime = None
ai_final_runtime = None
simple_final_runtime = None

def compute_ai_move():
    global ai_next_move, ai_computing, ai_move_ready
    ai_computing = True
    move = ai_player.get_next_move(ai_board, ai_board.get_queue())
    ai_next_move = move
    ai_move_ready = True
    ai_computing = False
    print("Thread finished computing AI move")

def draw_summary(center_x, center_y, board, runtime, screen):
    lines = board.lines_cleared
    text1 = bold_font.render("Game Over", True, (255, 0, 0))
    text2 = bold_font.render(f"Time: {runtime}s", True, (255, 255, 255))
    text3 = bold_font.render(f"Lines: {lines}", True, (255, 255, 255))

    screen.blit(text1, (center_x - text1.get_width() // 2, center_y - 40))
    screen.blit(text2, (center_x - text2.get_width() // 2, center_y))
    screen.blit(text3, (center_x - text3.get_width() // 2, center_y + 40))

def main():
    global fall_time, ai_next_move, ai_computing, ai_move_ready
    running = True
    simple_target_x = None
    simple_target_shape = None

    user_game_over = False
    ai_game_over = False
    simple_game_over = False

    while running:
        dt = clock.tick(FPS)
        fall_time += dt
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not user_game_over:
                if event.key == pygame.K_UP:
                    user_board.rotate()
                elif event.key == pygame.K_SPACE:
                    user_board.hard_drop_to_column()

        # Movement inputs
        if not user_game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                user_board.move_left()
            if keys[pygame.K_RIGHT]:
                user_board.move_right()
            if keys[pygame.K_DOWN]:
                user_board.soft_drop()

        # Game over detection and runtime locking
        if not user_game_over and user_board.is_game_over():
            user_game_over = True
            global user_final_runtime
            user_final_runtime = (pygame.time.get_ticks() - user_start_ticks) // 1000

        if not ai_game_over and ai_board.is_game_over():
            ai_game_over = True
            global ai_final_runtime
            ai_final_runtime = (pygame.time.get_ticks() - ai_start_ticks) // 1000

        if not simple_game_over and simple_h_board.is_game_over():
            simple_game_over = True
            global simple_final_runtime
            simple_final_runtime = (pygame.time.get_ticks() - simple_start_ticks) // 1000

        # Piece falling
        if fall_time > fall_speed:
            if not user_game_over:
                user_board.move_down()
            if not ai_game_over:
                ai_board.move_down()
            if not simple_game_over:
                simple_h_board.move_down()

            # AI handling
            if not ai_game_over:
                if not ai_computing and ai_next_move is None:
                    print("Thread started to compute AI move")
                    ai_thread = threading.Thread(target=compute_ai_move)
                    ai_thread.start()

                if ai_move_ready:
                    if ai_next_move is not None:
                        x, rotation = ai_next_move
                        print(f"AI placed at x={x}, rotation={rotation}")
                        ai_board.hard_drop_to_column(x, rotation)
                        ai_next_move = None
                        ai_move_ready = False

            # Simple heuristic AI
            if not simple_game_over and simple_target_x is None:
                piece = simple_h_board.current_piece.shape
                color = simple_h_board.current_piece.color
                x, y = simple_h_board.current_position
                grid = simple_h_board.grid
                queue = simple_h_board.get_queue()

                new_x, new_y, new_shape = simple.ai_move(x, y, piece, color, grid, queue, None)

                simple_target_x = new_x
                simple_target_shape = new_shape
                simple_h_board.current_piece.shape = new_shape
                simple_h_board.current_position = (new_x, y)
                simple_h_board.hard_drop_to_column(new_x)
                simple_target_x = None

            fall_time = 0

        # Compute runtime values
        user_runtime = user_final_runtime if user_game_over else (pygame.time.get_ticks() - user_start_ticks) // 1000
        ai_runtime = ai_final_runtime if ai_game_over else (pygame.time.get_ticks() - ai_start_ticks) // 1000
        simple_runtime = simple_final_runtime if simple_game_over else (pygame.time.get_ticks() - simple_start_ticks) // 1000

        # Draw boards
        user_board.draw(screen, USER_BOARD_X, USER_BOARD_Y, CELL_SIZE)
        ai_board.draw(screen, AI_BOARD_X, AI_BOARD_Y, CELL_SIZE)
        simple_h_board.draw(screen, SIMPLE_H_X, SIMPLE_H_Y, CELL_SIZE)

        # Draw line stats
        screen.blit(font.render(f"Lines: {user_board.lines_cleared}", True, (255, 255, 255)), (USER_BOARD_X, USER_BOARD_Y - 30))
        screen.blit(font.render(f"Lines: {ai_board.lines_cleared}", True, (255, 255, 255)), (AI_BOARD_X, AI_BOARD_Y - 30))
        screen.blit(font.render(f"Lines: {simple_h_board.lines_cleared}", True, (255, 255, 255)), (SIMPLE_H_X, SIMPLE_H_Y - 30))

        # Draw timers
        screen.blit(font.render(f"Time: {user_runtime}s", True, (255, 255, 255)), (USER_BOARD_X, USER_BOARD_Y - 60))
        screen.blit(font.render(f"Time: {ai_runtime}s", True, (255, 255, 255)), (AI_BOARD_X, AI_BOARD_Y - 60))
        screen.blit(font.render(f"Time: {simple_runtime}s", True, (255, 255, 255)), (SIMPLE_H_X, SIMPLE_H_Y - 60))

        # Draw summaries if game over
        if user_game_over:
            draw_summary(USER_BOARD_X + CELL_SIZE * 5, USER_BOARD_Y + CELL_SIZE * 10, user_board, user_runtime, screen)
        if ai_game_over:
            draw_summary(AI_BOARD_X + CELL_SIZE * 5, AI_BOARD_Y + CELL_SIZE * 10, ai_board, ai_runtime, screen)
        if simple_game_over:
            draw_summary(SIMPLE_H_X + CELL_SIZE * 5, SIMPLE_H_Y + CELL_SIZE * 10, simple_h_board, simple_runtime, screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
