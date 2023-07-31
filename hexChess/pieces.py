from board import HexBoard


def inc_y(pos: tuple, val: int):
    return pos[0], pos[1] + val


class Piece:
    def __init__(self, pos: tuple, side: str, board: HexBoard):
        if type(self) is Piece:
            raise Exception('Piece is an abstract class and cannot be instantiated directly')
        self.pos = pos
        self.side = side
        self.board = board


class Pawn(Piece):
    def __init__(self, pos: tuple, side: str, board: HexBoard):
        super().__init__(pos, side, board)

    def __repr__(self):
        return f"<{self.side} Pawn Object with pos {self.pos}>"

    def get_moves(self):
        if self.side == 'B':
            return self.moves_black()
        else:
            return self.moves_white()

    def moves_black(self):
        moves = set()
        test = inc_y(self.pos, -1)
        if self.board.is_clear(test):
            moves.add(test)
            if self.pos[1] == 7:  # black pawns can move two squares on seventh row
                test = inc_y(test, -1)
                if self.board.is_clear(test):
                    moves.add(test)

        p = self.board.get_piece((self.pos[0] + 1, self.pos[1]))
        if p is not None and p.side != self.side:
            moves.add((self.pos[0] + 1, self.pos[1]))
        p = self.board.get_piece((self.pos[0] - 1, self.pos[1] - 1))
        if p is not None and p.side != self.side:
            moves.add((self.pos[0] - 1, self.pos[1] - 1))

        return moves

    def moves_white(self):
        moves = set()
        test = inc_y(self.pos, 1)
        if self.board.is_clear(test):
            moves.add(test)
            if self.pos[0] - self.pos[1] == 1 and self.pos[0] <= 6 or self.pos in [(7, 4), (8, 3), (9, 2), (10, 1)]:
                test = inc_y(test, 1)
                if self.board.is_clear(test):
                    moves.add(test)

        p = self.board.get_piece((self.pos[0] - 1, self.pos[1]))
        if p is not None and p.side != self.side:
            moves.add((self.pos[0] - 1, self.pos[1]))
        p = self.board.get_piece((self.pos[0] + 1, self.pos[1] + 1))
        if p is not None and p.side != self.side:
            moves.add((self.pos[0] + 1, self.pos[1] + 1))

        return moves



