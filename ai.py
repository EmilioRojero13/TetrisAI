from board import Board
from piece import PIECES, COLORS, ROTATION_LIMITS, Piece

class AI:
    def __init__(self):
        self.weights = {
            "aggregate_height": -0.798752914564018,
            "complete_lines": 0.522287506868767,
            "holes": -0.24921408023878,
            "bumpiness": -0.164626498034284
        }
        self.planned_moves = []

    def clone_board(self, board):
        new_board = Board(board.width, board.height)
        new_board.grid = [row.copy() for row in board.grid] 
        new_board.queue = board.queue.copy()
        new_board.current_piece = board.current_piece  
        new_board.current_position = board.current_position  
        return new_board
    
    def apply_move(self, board, piece_key, move):
        piece_shape = PIECES[piece_key].copy()  # importante
        piece_color = COLORS[piece_key]
        piece = Piece(piece_shape, piece_color)

        x, rotation = move
        for _ in range(rotation):
            piece.rotate()

        pos = (x, 3)
        while board.is_valid_position(piece, pos):
            pos = (pos[0], pos[1] + 1)
        pos = (pos[0], pos[1] - 1)

        # Verifica por si acaso que la posición final es válida
        if not board.is_valid_position(piece, pos):
            return  # o raise ValueError("Invalid final position")

        for dx, dy in piece.shape:
            bx, by = pos[0] + dx, pos[1] + dy
            if 0 <= bx < board.width and 0 <= by < board.height:
                board.grid[by][bx] = piece_color

        board.clear_lines()
            
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
    
    def get_next_move(self, board: Board, queue, depth=0):
        # Prepend the current falling piece to the queue
        if depth == 0:
            current_label = board.current_piece_label
            queue = [current_label] + queue

        if not queue or depth >= 3:
            return self.eval_function(board.grid)

        piece_key = queue[0]
        rest_queue = queue[1:]
        best_score = float('-inf')
        best_move = None

        for rotation in range(ROTATION_LIMITS[piece_key]):
            piece_shape = PIECES[piece_key]
            piece_color = COLORS[piece_key]

            piece = Piece(piece_shape.copy(), piece_color)

            # Rotate the piece before checking its width
            for _ in range(rotation):
                piece.rotate()

            piece_width = max(dx for dx, dy in piece.shape) + 1
            valid_range = board.width - piece_width + 1

            for x in range(valid_range):
                sim_board = self.clone_board(board)

                # Apply hard drop simulation
                pos = (x, 3)
                while sim_board.is_valid_position(piece, pos):
                    pos = (pos[0], pos[1] + 1)
                pos = (pos[0], pos[1] - 1)

                if not sim_board.is_valid_position(piece, pos):
                    continue

                self.apply_move(sim_board, piece_key, (x, rotation))

                score = self.get_next_move(sim_board, rest_queue, depth + 1)

                if depth == 0:
                    if score > best_score:
                        best_score = score
                        best_move = (x, rotation)
                else:
                    best_score = max(best_score, score)

        return best_move if depth == 0 else best_score
