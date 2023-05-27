# TODO: Figure out wall kicks; figure out infinity
from playfield import Playfield

JLTSZ_WALL_KICK_DATA = {"0>1": ((-1, 0), (-1, 1), (0, -2), (-1, -2)), "1>0": ((1, 0), (1, -1), (0, 2), (1, 2)),
                        "1>2": ((1, 0), (1, -1), (0, 2), (1, 2)), "2>1": ((-1, 0), (-1, 1), (0, -2), (-1, -2)),
                        "2>3": ((1, 0), (1, 1), (0, -2), (1, -2)), "3>2": ((-1, 0), (-1, -1), (0, 2), (-1, 2)),
                        "3>0": ((-1, 0), (-1, -1), (0, 2), (-1, 2)), "0>3": ((1, 0), (1, 1), (0, -2), (1, -2))}
I_WALL_KICK_DATA = {"0>1": ((-2, 0), (1, 0), (-2, -1), (1, 2)), "1>0": ((2, 0), (-1, 0), (2, 1), (-1, -2)),
                    "1>2": ((-1, 0), (2, 0), (-1, 2), (2, -1)), "2>1": ((1, 0), (-2, 0), (1, -2), (-2, 1)),
                    "2>3": ((2, 0), (-1, 0), (2, 1), (-1, -2)), "3>2": ((-2, 0), (1, 0), (-2, -1), (1, 2)),
                    "3>0": ((1, 0), (-2, 0), (1, -2), (-2, 1)), "0>3": ((-1, 0), (2, 0), (-1, 2), (2, -1))}


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
        self._coordinates = None
        if type(self) is Piece:
            raise Exception('Piece is an abstract class and cannot be instantiated directly')
        self._corner = (3, 21)  # x, y position of top left corner of 'hit-box' for rotations
        self._rotation = 0
        self._field = pf
        # all/most methods called on the piece will be with respect to the 'field', so it is also a field

    def get_corner_position(self):
        return self._corner

    def get_coordinates(self):
        return self._coordinates

    def left(self):
        """
        moves piece one to the left if possible, otherwise this function does not do anything
        :return: nothing
        """
        new = []
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0] - 1, coord[1]):
                return
            new.append((coord[0] - 1, coord[1]))
        self._coordinates = tuple(new)
        self._corner = (self._corner[0] - 1, self._corner[1])

    def right(self):
        """
        moves piece one to the right if possible
        :return: nothing
        """
        new = []
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0] + 1, coord[1]):
                return
            new.append((coord[0] + 1, coord[1]))
        self._coordinates = tuple(new)
        self._corner = (self._corner[0] + 1, self._corner[1])

    def drop(self):
        """
        drops the piece by one, if piece can no longer move down, places it on field
        :return: (boolean) true if piece was able to move
        """
        new = []
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0], coord[1] - 1):
                self._field.add_blocks(self._coordinates, self.get_colour())
                return False
            new.append((coord[0], coord[1] - 1))
        self._coordinates = tuple(new)
        self._corner = (self._corner[0], self._corner[1] - 1)
        return True

    def hard_drop(self):
        """
        calls drop over and over until it returns false
        :return: nothing
        """
        while self.drop():
            pass

    def rotate_right(self):
        """
        tries to rotate the piece right (using the SRS algorithm)
        :return: nothing
        """
        if self._rotation == 3:
            new_state = 0
        else:
            new_state = self._rotation + 1
        self._try_set_coords(self._get_rotation_coords(new_state), new_state)

    def rotate_left(self):
        """
        tries to rotate the piece right (using the SRS algorithm)
        :return: nothing
        """
        if self._rotation == 0:
            new_state = 3
        else:
            new_state = self._rotation - 1
        self._try_set_coords(self._get_rotation_coords(new_state), new_state)

    # abstract methods
    @staticmethod
    def get_colour():
        raise NotImplementedError("Subclass did not implement get_colour method")

    def _get_rotation_coords(self, order):
        raise NotImplementedError("Subclass did not implement _try_place method")

    # shared helper methods
    def _try_set_coords(self, coords, orientation):
        valid = True
        for x, y in coords:
            if not self._field.is_clear(x, y):
                valid = False
                break
        if valid:
            self._rotation = orientation
            self._coordinates = coords
            return True
        else:
            return False

    def _abs_coords(self, coords):
        """
        takes in list of 4 relative coordinates to corner point, turns them into absolute coordinates
        :param coords: (iterable) of x, y
        :return: (tuple) represents a possible value for self._coordinates
        """
        return tuple((self._corner[0] + x, self._corner[1] - y) for x, y in coords)


class IPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        # list of coordinates of each piece when spawning
        self._coordinates = ((3, 20), (4, 20), (5, 20), (6, 20))

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        if orientation == 0:
            relative_coordinates = ((0, 1), (1, 1), (2, 1), (3, 1))
        elif orientation == 1:
            relative_coordinates = ((2, 0), (2, 1), (2, 2), (2, 3))
        elif orientation == 2:
            relative_coordinates = ((0, 2), (1, 2), (2, 2), (3, 2))
        else:  # i == 3
            relative_coordinates = ((1, 0), (1, 1), (1, 2), (1, 3))
        return self._abs_coords(relative_coordinates)

    @staticmethod
    def get_colour():
        return 1, 237, 250


# TODO: fix coordinates to use tuple and have correct coordinates (x = x - 4, y = y - 1)

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
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[8, 21], [8, 22], [9, 21], [9, 22]]

    @staticmethod
    def get_piece_type():
        return "OPiece"


if __name__ == "__main__":
    playfield = Playfield()
    piece = IPiece(playfield)

    # MOVEMENT TEST
    # print(piece.get_coordinates(), piece.get_corner_position())
    # piece.drop()
    # print(piece.get_coordinates(), piece.get_corner_position())
    # piece.left()
    # print(piece.get_coordinates(), piece.get_corner_position())
    # piece.left()
    # piece.left()
    # piece.left()
    # print(piece.get_coordinates(), piece.get_corner_position())
    # piece.right()
    # print(piece.get_coordinates(), piece.get_corner_position())
    # piece.right()
    # piece.right()
    # piece.right()
    # piece.right()
    # piece.right()
    # piece.right()
    # piece.right()
    # print(piece.get_coordinates(), piece.get_corner_position())
    #
    # piece.hard_drop()

    # X, Y = field.get_dimensions()
    # for i_1 in range(Y):
    #     for j_1 in range(X):
    #         print(field.is_clear(j_1, Y - i_1 - 1), end="")
    #     print()

    # ROTATION TEST
    playfield.add_blocks(((4, 18), ), (0, 0, 0))
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    piece.rotate_right()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    piece.rotate_right()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    piece.rotate_right()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    piece.rotate_left()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    piece.rotate_left()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    piece.rotate_left()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
