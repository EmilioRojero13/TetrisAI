import pygame
import sys
from board import Board

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
fall_speed = 750  # milisegundos

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
            elif event.type == pygame.KEYDOWN:  # Detecta solo cuando se presiona la tecla
                if event.key == pygame.K_UP:  
                    user_board.rotate()

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
            fall_time = 0

        user_board.draw(screen, USER_BOARD_X, USER_BOARD_Y, CELL_SIZE)
        ai_board.draw(screen, AI_BOARD_X, AI_BOARD_Y, CELL_SIZE)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
