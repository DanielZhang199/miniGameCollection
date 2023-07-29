# piece objects are not implemented yet, so tests can't be written

class HexBoard:
    """
    Represents the current game state with pieces and their locations, as well as meta game data (turn, checks, etc.)
    """
    columns = "abcdefghijk"
    rows = [6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6]

    def __init__(self):
        self._pieces = {}  # stores location of each piece
        # todo: add pieces to board here
        self._previous = []
        self._kings = ["f1", "f11"]  # king locations [white, black]

        # immutable attributes
        self.turn = "W"
        self.status = None

    def _add_piece(self, piece):
        if piece.pos in self._pieces:
            raise RuntimeError("Trying to place piece where one already exists!")
        self._pieces[piece.pos] = piece

    def get_piece(self, pos: str):
        """
        gets piece on specified square; returns None if square is empty or does not exist
        :param pos: (str) valid algebraic coordinates
        :return: (Piece)
        """
        return self._pieces.get(pos, None)

    def exists_piece(self, pos: str):
        """
        True if the square is occupied by a piece
        :param pos: (str)
        :return: (bool)
        """
        return pos in self._pieces

    def update(self, piece, flag):
        """
        moves piece to new position changes which turn it is, taking into account captures and special moves
        :param piece: (Piece) which has moved
        :param flag: (str) special considerations for special moves (i.e. promotion or en passant or castling)
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

