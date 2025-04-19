from board import Board
from piece import PIECES, COLORS, Piece

class AI:
    def __init__(self):
        self.weights = {
            "aggregate_height": -0.798752914564018,
            "complete_lines": 0.522287506868767,
            "holes": -0.24921408023878,
            "bumpiness": -0.164626498034284
        }

    def clone_board(self, board):
        new_board = Board(board.width, board.height)
        new_board.grid = [row.copy() for row in board.grid] 
        new_board.queue = board.queue.copy()
        new_board.current_piece = board.current_piece  
        new_board.current_position = board.current_position  
        return new_board
    
    def apply_move(self, board, piece_key, move):
        piece_shape = PIECES[piece_key]
        piece_color = COLORS[piece_key]
        piece = Piece(piece_shape, piece_color)

        x, rotation = move
        rotated_piece = Piece(piece_shape.copy(), piece_color)
        rotated_piece.rotate(rotation)

        pos = (x, 0)
        while board.is_valid_position(rotated_piece, pos):
            pos = (pos[0], pos[1] + 1) 
        pos = (pos[0], pos[1] - 1)

        for dx, dy in rotated_piece.shape:
            bx, by = pos[0] + dx, pos[1] + dy
            if 0 <= bx < board.width and 0 <= by < board.height:
                board.grid[by][bx] = piece_color

    def choose_best_move(self, board, piece_key):
        best_score = float('-inf')
        best_move = None

        piece_shape = PIECES[piece_key]
        piece_color = COLORS[piece_key]
        piece = Piece(piece_shape, piece_color)

        for rotation in range(4): 
            for x in range(board.width): 
                sim_board = self.clone_board(board)  

                self.apply_move(sim_board, piece_key, (x, rotation))

                score = self.evaluate_board(sim_board.grid)

                if score > best_score:
                    best_score = score
                    best_move = (x, rotation)

        return best_move
    
    def plan_moves(self, board: Board, queue: list[str]):
        self.planned_moves = []
        sim_board = self.clone_board(board)

        for i in range(len(queue)): 
            piece_key = queue[i]
            best_move = self.choose_best_move(sim_board, piece_key)
            self.planned_moves.append(best_move)

            self.apply_move(sim_board, piece_key, best_move)

    def get_next_move(self, board, next_piece_key):
        if self.planned_moves:
            return self.planned_moves.pop(0)  # Retorna el siguiente movimiento planeado
        else:
            # Si no hay movimientos planeados, planifica de nuevo
            self.plan_moves(board, board.queue)
            return self.planned_moves.pop(0)

    
    def compute_aggregate_height(self, board):
        width = 10
        height = 20
        total_height = 0

        for x in range(width):
            column_height = 0
            for y in range(height):
                if board[y][x] is not None:
                    column_height = height - y
                    break
            total_height += column_height

        return total_height
    
    def count_complete_lines(self, board):
        count = 0
        for row in board:
            is_complete = True
            for cell in row:
                if cell is None:
                    is_complete = False
                    break
            if is_complete:
                count += 1
        return count

    def count_holes(self, board):
        width = 10
        height = 20
        holes = 0

        for x in range(width):
            block_found = False
            for y in range(height):
                if board[y][x] is not None:
                    block_found = True
                elif board[y][x] is None and block_found:
                    holes += 1

        return holes
    
    def compute_bumpiness(self, board):
        width = 10
        height = 20
        heights = []

        for x in range(width):
            column_height = 0
            for y in range(height):
                if board[y][x] is not None:
                    column_height = height - y
                    break
            heights.append(column_height)

        bumpiness = 0
        for i in range(width - 1):
            bumpiness += abs(heights[i] - heights[i + 1])

        return bumpiness
    
    def eval_function(self, board):
        agg_height = self.compute_aggregate_height(board)
        lines = self.count_complete_lines(board)
        holes = self.count_holes(board)
        bumpiness = self.compute_bumpiness(board)

        score = (
            self.weights["aggregate_height"] * agg_height +
            self.weights["complete_lines"] * lines +
            self.weights["holes"] * holes +
            self.weights["bumpiness"] * bumpiness
        )
        return score
