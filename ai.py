from board import Board
from piece import Piece, PIECES, COLORS, ROTATION_LIMITS
import sys
import pygame

class AI:
    def __init__(self):
        self.weights = {
            # "aggregate_height": -0.798752914564018,
            # "complete_lines": 0.522287506868767,
            # "holes": -0.24921408023878,
            # "bumpiness": -0.164626498034284
            # "aggregate_height": -0.9,
            # "complete_lines": 0.72,
            # "holes": -0.45,
            # "bumpiness": -0.12
            "aggregate_height": -0.6,
            "complete_lines": 0.85,
            "holes": -0.6,
            "bumpiness": -0.25
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
        piece_shape = PIECES[piece_key]
        piece_color = COLORS[piece_key]
        piece = Piece(piece_shape.copy(), piece_color)

        x, rotation = move
        for _ in range(rotation):
            piece.rotate()

        pos = (x, 3)
        while board.is_valid_position(piece, pos):
            pos = (pos[0], pos[1] + 1)
        pos = (pos[0], pos[1] - 1)

        for dx, dy in piece.shape:
            bx, by = pos[0] + dx, pos[1] + dy
            if 0 <= bx < board.width and 0 <= by < board.height:
                board.grid[by][bx] = piece_color

        board.clear_lines()  

    def choose_best_move(self, board, piece_key):
        best_score = float('-inf')
        best_move = None
        sim_board = None

        for rotation in range(ROTATION_LIMITS[piece_key]):

            piece_shape = PIECES[piece_key]
            piece_color = COLORS[piece_key]
            test_piece = Piece(piece_shape.copy(), piece_color)
            for _ in range(rotation):
                test_piece.rotate()

            piece_width = max(x for x, y in test_piece.shape) + 1
            valid_x_range = board.width - piece_width + 1

            for x in range(valid_x_range):
                sim_board = self.clone_board(board)
                try:
                    # print(f"Trying piece {piece_key} at x={x}, rotation={rotation}")

                    piece = Piece(piece_shape.copy(), piece_color)
                    for _ in range(rotation):
                        piece.rotate()

                    pos = (x, 3)
                    while sim_board.is_valid_position(piece, pos):
                        pos = (pos[0], pos[1] + 1)
                    pos = (pos[0], pos[1] - 1)

                    if not sim_board.is_valid_position(piece, pos):
                        # print(f"Invalid final position at x={x}, rotation={rotation}, skipping...")
                        continue

                    self.apply_move(sim_board, piece_key, (x, rotation))
                    # print("Board after move:")
                    # for i in sim_board.grid:
                    #     print(i)

                    score = self.eval_function(sim_board.grid)
                    # print(f"Score: {score}")
                    if score > best_score:
                        best_score = score
                        best_move = (x, rotation)
                except Exception as e:
                    # print(f"Exception at x={x}, rotation={rotation}: {e}")
                    continue
        return best_move

    def initial_deep_rollout(self, board, queue, initial_move, initial_piece_label):
        self.planned_moves.clear()
        sim_board = self.clone_board(board)
        self.apply_move(sim_board, initial_piece_label, initial_move)


        for piece_key in queue:
            best_move = self.choose_best_move(sim_board, piece_key)
            if best_move is None:
                break  
            self.planned_moves.append(best_move)
            self.apply_move(sim_board, piece_key, best_move)

            # print("final would be")
            # print(best_move)
            # print(piece_key)
            # for i in sim_board.grid:
            #     print(i)

    def incremental_plan(self, board, new_piece_key):
        sim_board = self.clone_board(board)
        for i, move in enumerate(self.planned_moves):
            if i < len(board.queue): 
                piece_key = board.queue[i]
                self.apply_move(sim_board, piece_key, move)

        best_move = self.choose_best_move(sim_board, new_piece_key)
        self.planned_moves.append(best_move)

    def get_next_move(self, board):
        print(f"CURRENT PLANNED QUEUE: {board.queue}")
        print(f"CURRENT PLANNED MOVES: {self.planned_moves[1:]}")
        if not self.planned_moves:
            initial_move = self.choose_best_move(board, board.current_piece_label)
            self.initial_deep_rollout(board, board.queue, initial_move, board.current_piece_label)
            return initial_move
        else:
            print("INCREMENTAL DECISION")
            print(f"planning now for: {board.queue[4]}")
            move_to_return = self.planned_moves.pop(0)
            self.incremental_plan(board, board.queue[4])  

        return move_to_return

    def compute_aggregate_height(self, board):
        width = 10
        height = 20
        total_height = 0
        for x in range(width):
            for y in range(height):
                if board[y][x] is not None:
                    total_height += height - y
                    break
        return total_height

    def count_complete_lines(self, board):
        count = 0
        for row in board:
            if all(cell is not None for cell in row):
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
                elif block_found:
                    holes += 1
        return holes

    def compute_bumpiness(self, board):
        height = 20
        width = 10
        heights = []
        for x in range(width):
            h = 0
            for y in range(height):
                if board[y][x] is not None:
                    h = height - y
                    break
            heights.append(h)
        return sum(abs(heights[i] - heights[i + 1]) for i in range(width - 1))

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
