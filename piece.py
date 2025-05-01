PIECES = {
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "Z": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "S": [(1, 0), (0, 0), (0, 1), (-1, 1)],
    "J": [(-1, 0), (0, 0), (1, 0), (1, 1)],
    "L": [(-1, 0), (0, 0), (1, 0), (-1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
}

COLORS = {
    "O": (255, 255, 0),
    "I": (0, 255, 255),
    "S": (0, 255, 0),
    "Z": (255, 0, 0),
    "J": (255, 165, 0),
    "L": (0, 0, 255),
    "T": (128, 0, 128),
}

ROTATION_LIMITS = {
    "O": 1,
    "I": 2,
    "S": 2,
    "Z": 2,
    "T": 4,
    "L": 4,
    "J": 4,
}

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color

    def rotate(self, times=1):
        for _ in range(times):
            # print("rotating")
            self.shape = [(-dy, dx) for dx, dy in self.shape]