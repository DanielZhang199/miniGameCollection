# piece objects are not implemented yet, so tests can't be written

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
        :param piece: (Piece) which has moved
        :param move: (str) position of piece after move
        :param flag: (int) 0 for castling, 1 for enpassant, 'Q', 'R', 'N', 'B' for promotion
        :return:
        """
        pass

    def is_check(self):
        """
        returns True if the current moving side is in check
        :return: (bool)
        """
        pass

    def check_status(self):
        """
        checks if the game is over, returns True if it is, updates self.status to the game result
        :return:
        """
        pass

    def undo(self):
        """
        undoes the last move; in future there will likely be a way to redo (but not a complicated version control
        multiple timeline kind of system)
        :return:
        """
        pass


if __name__ == "__main__":
    from pieces import Pawn
    board = HexBoard()
    board._add_piece(Pawn((2, 1), "W", board))
    board._add_piece(Pawn((3, 2), "B", board))
    print(board.is_clear((2, 1)))
    print(board.is_clear((2, 2)))
    print(board.is_clear((2, 0)))
    print(board.get_piece((2, 1)).get_moves())
    print(board.get_piece((1, 1)).get_moves())
    print(board.get_piece((3, 2)).get_moves())

