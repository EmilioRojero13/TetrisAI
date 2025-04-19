import pygame
import sys
from board import Board
from ai import AI

# Inicializar Pygame
pygame.init()

# Constantes de la ventana
WIDTH, HEIGHT = 900, 650
FPS = 10
BACKGROUND_COLOR = (0, 0, 0)
CELL_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20

USER_BOARD_X, USER_BOARD_Y = 100, 50
AI_BOARD_X, AI_BOARD_Y = 550, 50

# Crear la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris AI vs Player")

# Reloj para controlar FPS
clock = pygame.time.Clock()

user_board = Board(GRID_WIDTH, GRID_HEIGHT)
ai_board = Board(GRID_WIDTH, GRID_HEIGHT)
fall_time = 0
fall_speed = 2000  # milisegundos
ai_player = AI()

def main():
    global fall_time
    running = True
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
                if event.key == pygame.K_SPACE:
                    user_board.hard_drop_to_column()


        keys = pygame.key.get_pressed()  

        if keys[pygame.K_LEFT]: 
            user_board.move_left()
        if keys[pygame.K_RIGHT]: 
            user_board.move_right()
        if keys[pygame.K_DOWN]: 
            user_board.soft_drop()
        
        if fall_time > fall_speed:

            # user_board.move_down() DESCOMENTAR

            ai_move = ai_player.get_next_move(ai_board)
            print(ai_move)

            ai_board.hard_drop_to_column(ai_move[0], ai_move[1])

            fall_time = 0
   


        user_board.draw(screen, USER_BOARD_X, USER_BOARD_Y, CELL_SIZE)
        ai_board.draw(screen, AI_BOARD_X, AI_BOARD_Y, CELL_SIZE)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
