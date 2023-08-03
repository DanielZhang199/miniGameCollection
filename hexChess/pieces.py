from board import HexBoard


def scan_orthogonal(board: HexBoard, start_pos: tuple, side: str):
    """
    scans all three orthogonal directions in board stopping at first obstacle
    (including obstacle if it is an enemy piece), returning all pieces
    """
    result = set()
    x, y = start_pos
    while True:  # up
        y += 1
        if not board.is_clear((x, y)):
            if board.capturable_by((x, y)) == side:
                result.add((x, y))
            break
        result.add((x, y))

    y = start_pos[1]
    while True:
        y -= 1  # down
        if not board.is_clear((x, y)):
            if board.capturable_by((x, y)) == side:
                result.add((x, y))
            break
        result.add((x, y))

    x, y = start_pos
    while True:  # up-left
        if x > 6:
            y += 1
        x -= 1
        if not board.is_clear((x, y)):
            if board.capturable_by((x, y)) == side:
                result.add((x, y))
            break
        result.add((x, y))

    x, y = start_pos
    while True:  # up-left
        if x < 6:
            y += 1
        x += 1
        if not board.is_clear((x, y)):
            if board.capturable_by((x, y)) == side:
                result.add((x, y))
            break
        result.add((x, y))

    x, y = start_pos
    while True:  # down-left
        if x <= 6:
            y -= 1
        x -= 1
        if not board.is_clear((x, y)):
            if board.capturable_by((x, y)) == side:
                result.add((x, y))
            break
        result.add((x, y))

    x, y = start_pos
    while True:  # down-right
        if x >= 6:
            y -= 1
        x += 1
        if not board.is_clear((x, y)):
            if board.capturable_by((x, y)) == side:
                result.add((x, y))
            break
        result.add((x, y))

    return result


class Rook:
    def __init__(self, pos: tuple, side: str, board: HexBoard):
        self.pos = pos
        self.side = side
        self._board = board

    def __repr__(self):
        return f"<{self.side} Rook Object with pos {self.pos}>"

    def get_moves(self):
        return scan_orthogonal(self._board, self.pos, self.side)


class Pawn:
    def __init__(self, pos: tuple, side: str, board: HexBoard):
        self.pos = pos
        self.side = side
        self._board = board

    def __repr__(self):
        return f"<{self.side} Pawn Object with pos {self.pos}>"

    def get_moves(self):
        if self.side == 'B':
            return self.moves_black()
        else:
            return self.moves_white()

    def moves_black(self):
        moves = set()
        if self._board.is_clear((self.pos[0], self.pos[1] - 1)):
            moves.add((self.pos[0], self.pos[1] - 1))
            if self.pos[1] == 7:  # black pawns can move two squares on seventh row
                if self._board.is_clear((self.pos[0], self.pos[1] - 2)):
                    moves.add((self.pos[0], self.pos[1] - 2))

        # check sideways movements for captures
        if self._board.capturable_by((self.pos[0] + 1, self.pos[1])) == self.side:
            moves.add((self.pos[0] + 1, self.pos[1]))
        if self._board.capturable_by((self.pos[0] - 1, self.pos[1] - 1)) == self.side:
            moves.add((self.pos[0] - 1, self.pos[1] - 1))

        return moves

    def moves_white(self):
        moves = set()
        if self._board.is_clear((self.pos[0], self.pos[1] + 1)):
            moves.add((self.pos[0], self.pos[1] + 1))
            if self.pos[0] - self.pos[1] == 1 and self.pos[0] <= 6 or self.pos in [(7, 4), (8, 3), (9, 2), (10, 1)]:
                if self._board.is_clear((self.pos[0], self.pos[1] + 2)):
                    moves.add((self.pos[0], self.pos[1] + 2))

        if self._board.capturable_by((self.pos[0] - 1, self.pos[1])) == self.side:
            moves.add((self.pos[0] - 1, self.pos[1]))
        if self._board.capturable_by((self.pos[0] + 1, self.pos[1] + 1)) == self.side:
            moves.add((self.pos[0] + 1, self.pos[1] + 1))

        return moves



