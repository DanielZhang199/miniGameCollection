# There will be no wall kicks, because I still don't understand how it works
from random import choice
from playfield import Playfield

COLOURS = ((253, 63, 89), (255, 200, 46), (254, 251, 52), (83, 218, 63), (1, 237, 250), (221, 10, 178))


def num_to_piece(pf: Playfield, n: int):
    """
    turns the number given by the bag into a piece object
    :param pf: current board; part of piece constructor
    :param n: output from bag (integer between 0-6)
    :return: Piece object
    """
    if n == 0:
        return TPiece(pf)
    elif n == 1:
        return IPiece(pf)
    elif n == 2:
        return JPiece(pf)
    elif n == 3:
        return LPiece(pf)
    elif n == 4:
        return ZPiece(pf)
    elif n == 5:
        return SPiece(pf)
    else:
        return OPiece(pf)


class Piece:
    def __init__(self, pf: Playfield):
        if type(self) is Piece:
            raise Exception('Piece is an abstract class and cannot be instantiated directly')
        self._corner = [7, 22]  # x, y position of top left corner of 'hit-box' for rotations
        self._rotation = 0
        self._colour = choice(COLOURS)
        self._field = pf
        # all/most methods called on the piece will be with respect to the 'field', so it is also a field

    def get_corner_position(self):
        return self._corner

    def get_colour(self):
        return self._colour


class IPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        # list of coordinates of each piece
        self._coordinates = [[7, 21], [8, 21], [9, 21], [10, 21]]

    @staticmethod
    def get_piece_type():
        return "IPiece"

    # TODO: following functions
    def drop(self):
        """
        drops the piece by one
        :return: (boolean) true if piece was able to move
        """
        pass

    def rotate(self):
        """
        tries to rotate the piece (using the SRS algorithm)
        :return: nothing
        """
        pass

    def hard_drop(self):
        """
        calls drop over and over until it returns false
        :return: nothing
        """
        pass

    def left(self):
        """
        moves piece one to the left if possible, otherwise this function does not do anything
        :return: nothing
        """
        pass

    def right(self):
        """
        moves piece one to the right if possible
        :return: nothing
        """
        pass


class ZPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[7, 22], [8, 22], [8, 21], [9, 21]]

    @staticmethod
    def get_piece_type():
        return "ZPiece"


class SPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[7, 21], [8, 21], [8, 22], [9, 22]]

    @staticmethod
    def get_piece_type():
        return "SPiece"


class TPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[7, 21], [8, 21], [8, 22], [9, 21]]

    @staticmethod
    def get_piece_type():
        return "TPiece"


class LPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[7, 21], [8, 21], [9, 21], [9, 22]]

    @staticmethod
    def get_piece_type():
        return "LPiece"


class JPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[7, 21], [7, 22], [8, 21], [9, 21]]

    @staticmethod
    def get_piece_type():
        return "JPiece"


class OPiece(Piece):
    def __init__(self):
        super().__init__()
        self._coordinates = [[8, 21], [8, 22], [9, 21], [9, 22]]

    @staticmethod
    def get_piece_type():
        return "OPiece"
