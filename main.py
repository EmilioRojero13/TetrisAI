import pygame
import sys
import threading
from board import Board
from ai import AI
import simple

pygame.init()

WIDTH, HEIGHT = 1500, 650
FPS = 10
BACKGROUND_COLOR = (0, 0, 0)
CELL_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20

USER_BOARD_X, USER_BOARD_Y = 100, 50
AI_BOARD_X, AI_BOARD_Y = 550, 50
SIMPLE_H_X , SIMPLE_H_Y = 1000, 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris AI vs Player")

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

def compute_ai_move():
    global ai_next_move, ai_computing, ai_move_ready
    ai_computing = True
    move = ai_player.get_next_move(ai_board, ai_board.get_queue())
    ai_next_move = move
    ai_move_ready = True
    ai_computing = False
    print("Thread finished computing AI move")

def main():
    global fall_time, ai_next_move, ai_computing, ai_move_ready
    running = True
    simple_target_x = None
    simple_target_shape = None

    while running:
        dt = clock.tick(FPS)
        fall_time += dt
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    user_board.rotate()
                elif event.key == pygame.K_SPACE:
                    user_board.hard_drop_to_column()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            user_board.move_left()
        if keys[pygame.K_RIGHT]:
            user_board.move_right()
        if keys[pygame.K_DOWN]:
            user_board.soft_drop()

        if fall_time > fall_speed:
            user_board.move_down()
            ai_board.move_down()
            simple_h_board.move_down()

            if not ai_computing and ai_next_move is None:
                print("Thread started to compute AI move")
                ai_thread = threading.Thread(target=compute_ai_move)
                ai_thread.start()

            if ai_move_ready:
                if ai_next_move is not None:
                    x, rotation = ai_next_move
                    print(f"Piece placed at x={x}, rotation={rotation}")
                    ai_board.hard_drop_to_column(x, rotation)
                    ai_next_move = None
                    ai_move_ready = False
                else:
                    print("AI move not ready yet.")
                    
            
            # Check if we need a new move for simple_h_board
            if simple_target_x is None:
                simple_piece = simple_h_board.current_piece.shape
                simple_color = simple_h_board.current_piece.color
                simple_x, simple_y = simple_h_board.current_position
                simple_grid = simple_h_board.grid
                simple_queue = simple_h_board.get_queue()

                new_x, new_y, new_shape = simple.ai_move(simple_x, simple_y, simple_piece, simple_color, simple_grid, simple_queue, None)

                simple_target_x = new_x
                simple_target_shape = new_shape
                simple_h_board.current_piece.shape = simple_target_shape
                simple_h_board.current_position = (simple_target_x, simple_h_board.current_position[1])

            # # Step-by-step drop
            # prev_y = simple_h_board.current_position[1]
            # simple_h_board.soft_drop()

            # # If locked, reset target
            # if simple_h_board.current_position[1] == prev_y:  # no move = piece locked
            #     simple_target_x = None
            #     simple_target_shape = None

            fall_time = 0

        user_board.draw(screen, USER_BOARD_X, USER_BOARD_Y, CELL_SIZE)
        ai_board.draw(screen, AI_BOARD_X, AI_BOARD_Y, CELL_SIZE)
        simple_h_board.draw(screen, SIMPLE_H_X,SIMPLE_H_Y,CELL_SIZE)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()