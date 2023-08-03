from pieces import *


class HexBoard:
    """
    Represents the current game state with pieces and their locations, as well as meta game data (turn, checks, etc.)
    """
    rows = [6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6]

    def __init__(self):
        self._pieces = {}  # stores location of each piece
        # todo: add pieces to board here
        self._previous = []
        self._kings = [(6, 1), (6, 11)]  # king locations [white, black]

        # immutable attributes
        self.turn = "W"
        self.status = None

    def _add_piece(self, piece):
        if piece.pos in self._pieces:
            raise RuntimeError("Trying to place piece where one already exists!")
        self._pieces[piece.pos] = piece

    def get_piece(self, pos: tuple):
        """
        gets piece on specified square; returns None if square is empty or does not exist
        :param pos: (str) valid algebraic coordinates
        :return: (Piece)
        """
        return self._pieces.get(pos, None)

    def capturable_by(self, pos):
        """
        returns opposite side of piece on the position (i.e. the side that can capture the piece)
        or False if no piece is on the square
        :param pos:
        :return:
        """
        p = self._pieces.get(pos, None)
        if p is None:
            return False
        if p.side == "W":
            return "B"
        return "W"

    def is_clear(self, pos: tuple):
        """
        False if the square is occupied by a piece or is out of bounds
        :param pos: (str)
        :return: (bool)
        """
        if 1 <= pos[0] <= 11 and 1 <= pos[1] <= self.rows[pos[0] - 1]:
            return pos not in self._pieces
        return False

    def update(self, piece, move, flag=None):
        """
        moves piece to new position changes which turn it is, taking into account captures and special moves
        will return string for 'check', 'checkmate', 'stalemate', 'promotion', and 'insufficient material'
        :param piece: (Piece) which has moved
        :param move: (str) position of piece after move
        :param flag: (int) 0 for castling, 1 for enpassant, 'Q', 'R', 'N', 'B' for promotion
        :return: (str)
        """
        pass

    def is_check(self):
        """
        returns True if the current moving side is in check
        :return: (bool)
        """
        pass

    def test_check(self, start, end):
        """
        returns true if the attempted move leads to check
        THE COORDINATES ENTERED NEED TO BE TO A VALID MOVE A PIECE CAN MAKE
        :param start: (tuple) coordinates of a square with piece
        :param end: (tuple) coordinates of a square the piece can move to
        :return: (bool)
        """

    def undo(self):
        """
        undoes the last move; in future there will likely be a way to redo (but not a complicated version control
        multiple timeline kind of system)
        :return:
        """
        pass

    def get_legal_moves(self, pos):
        """
        returns set of all legal moves (squares) a piece at the x, y position can make, empty set if no piece is there
        :param pos: (tuple)
        :return: (set) of coordinates (tuple)
        """
        p = self.get_piece(pos)
        if p is None:
            return set()
        # result = set()
        return p.get_moves()  # temporary


if __name__ == "__main__":

    board = HexBoard()
    board._add_piece(Pawn((2, 1), "W", board))
    board._add_piece(Rook((3, 2), "B", board))
    board._add_piece(Pawn((3, 6), "W", board))
    print(board.get_legal_moves((2, 1)))
    print(sorted(list(board.get_legal_moves((3, 2)))))

