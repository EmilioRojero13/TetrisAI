import pygame
from piece import PIECES, COLORS, Piece
import random

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BORDER_THICKNESS = 2

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.current_position = (0, 0)
        self.current_piece_label = None
        self.queue = self.init_queue()
        self.spawn_new_piece()

    def init_queue(self):
        m = []
        for _ in range(5):
            m.append(random.choice(list(PIECES.keys())))
        return m

    def is_valid_position(self, piece, pos):
        for dx, dy in piece.shape:
            x = pos[0] + dx
            y = pos[1] + dy
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            if self.grid[y][x] is not None:
                return False
        return True

    def spawn_new_piece(self):
        piece_type = self.queue.pop(0)
        last_in_queue = random.choice(list(PIECES.keys()))
        self.queue.append(last_in_queue)
        shape = PIECES[piece_type]
        color = COLORS[piece_type]
        self.current_piece = Piece(shape, color)
        self.current_piece_label = piece_type
        self.current_position = (self.width // 2, 0)

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = self.height - len(new_grid)
        new_rows = [[None] * self.width for _ in range(lines_cleared)]
        self.grid = new_rows + new_grid

    def lock_piece(self):
        for dx, dy in self.current_piece.shape:
            x = self.current_position[0] + dx
            y = self.current_position[1] + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = self.current_piece.color

    def move_down(self):
        new_pos = (self.current_position[0], self.current_position[1] + 1)
        if self.is_valid_position(self.current_piece, new_pos):
            self.current_position = new_pos
        else:
            self.lock_piece()
            self.clear_lines()
            self.spawn_new_piece()

    def draw(self, screen, offset_x, offset_y, cell_size):
        for row in range(self.height):
            for col in range(self.width):
                rect = pygame.Rect(
                    offset_x + col * cell_size,
                    offset_y + row * cell_size,
                    cell_size,
                    cell_size
                )

                if self.grid[row][col] is not None:
                    color = self.grid[row][col]
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # borde de pieza colocada
                else:
                    pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # solo borde de celda vacía

        if self.current_piece:
            for dx, dy in self.current_piece.shape:
                x = self.current_position[0] + dx
                y = self.current_position[1] + dy
                rect = pygame.Rect(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(screen, self.current_piece.color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # borde de la pieza actual

    def move_left(self):
        new_pos = (self.current_position[0] - 1, self.current_position[1])
        if self.is_valid_position(self.current_piece, new_pos):
            self.current_position = new_pos

    def move_right(self):
        new_pos = (self.current_position[0] + 1, self.current_position[1])
        if self.is_valid_position(self.current_piece, new_pos):
            self.current_position = new_pos

    def soft_drop(self):
        new_pos = (self.current_position[0], self.current_position[1] + 1)
        if self.is_valid_position(self.current_piece, new_pos):
            self.current_position = new_pos
        else:
            self.lock_piece()
            self.clear_lines()
            self.spawn_new_piece()

    def rotate(self, rotation=1, force=False):
        rotated_piece = Piece(self.current_piece.shape.copy(), self.current_piece.color)
        for _ in range(rotation):
            rotated_piece.rotate()
        
        if force or self.is_valid_position(rotated_piece, self.current_position):
            self.current_piece = rotated_piece


    def hard_drop_to_column(self,x=None, rotation=0):
        self.rotate(rotation, force=True)  # Rota la pieza si es necesario
        if not x:
            pos = (self.current_position[0], self.current_position[1])  # Empieza desde la parte superior de la columna deseada
        else:
            pos = (x, 0)

        # Baja la pieza hasta el fondo de la columna
        while self.is_valid_position(self.current_piece, (pos[0], pos[1] + 1)):
            pos = (pos[0], pos[1] + 1)

        # Coloca la pieza en la fila más baja posible en esa columna
        self.current_position = pos
        self.lock_piece()
        self.clear_lines()
        self.spawn_new_piece()