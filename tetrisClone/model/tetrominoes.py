# TODO: figure out infinity
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
        self._corner = [3, 21]  # x, y position of top left corner of 'hit-box' for rotations
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
        self._move(-1)

    def right(self):
        """
        moves piece one to the right if possible
        :return: nothing
        """
        self._move(1)

    def _move(self, n):
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0] + n, coord[1]):
                return
        for coord in self._coordinates:
            coord[0] += n
        self._corner[0] += n

    def drop(self):
        """
        drops the piece by one, if piece can no longer move down, places it on field
        :return: (boolean) true if piece was able to move
        """
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0], coord[1] - 1):
                self._field.add_blocks(self._coordinates, self.get_colour())
                return False
        for coord in self._coordinates:
            coord[1] -= 1
        self._corner[1] -= 1
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
        self._perform_rotate(self._get_rotation_coords(new_state), new_state)

    def rotate_left(self):
        """
        tries to rotate the piece right (using the SRS algorithm)
        :return: nothing
        """
        if self._rotation == 0:
            new_state = 3
        else:
            new_state = self._rotation - 1
        self._perform_rotate(self._get_rotation_coords(new_state), new_state)

    # abstract methods
    @staticmethod
    def get_colour():
        raise NotImplementedError("Subclass did not implement get_colour method")

    def _get_rotation_coords(self, order):
        raise NotImplementedError("Subclass did not implement _try_place method")

    # shared helper methods
    def _perform_rotate(self, coords, orientation):
        if self._try_set_coords(coords):
            # helper function above sets coordinates, we only need to change rotation value
            self._rotation = orientation
        else:
            kicks = self._get_kicks(orientation)
            for dx, dy in kicks:
                if self._try_set_coords([[x + dx, y + dy] for x, y in coords]):
                    print("KICK PERFORMED")
                    self._rotation = orientation
                    self._corner[0] += dx
                    self._corner[1] += dy
                    return

    def _try_set_coords(self, coords):
        valid = True
        for x, y in coords:
            if not self._field.is_clear(x, y):
                valid = False
                break
        if valid:
            self._coordinates = coords
            return True
        return False

    def _abs_coords(self, coords):
        """
        takes in list of 4 relative coordinates to corner point, turns them into absolute coordinates
        :param coords: (iterable) of x, y
        :return: (tuple) represents a possible value for self._coordinates
        """
        return [[self._corner[0] + x, self._corner[1] - y] for x, y in coords]

    def _get_kicks(self, orientation):
        return JLTSZ_WALL_KICK_DATA[str(self._rotation) + ">" + str(orientation)]


class IPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        # list of coordinates of each piece when spawning
        self._coordinates = [[3, 20], [4, 20], [5, 20], [6, 20]]

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

    def _get_kicks(self, orientation):
        return I_WALL_KICK_DATA[str(self._rotation) + ">" + str(orientation)]

    @staticmethod
    def get_colour():
        return 1, 237, 250  # Cyan


# TODO: fix coordinates to use tuple and have correct coordinates (x = x - 4, y = y - 1)

class ZPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 21], [4, 21], [4, 22], [5, 22]]

    # TODO: this
    def _get_rotation_coords(self, order):
        pass

    @staticmethod
    def get_colour():
        return 253, 63, 89  # Salmon


class SPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [4, 20], [4, 21], [5, 21]]

    # TODO: this
    def _get_rotation_coords(self, order):
        pass

    @staticmethod
    def get_colour():
        return 83, 218, 63  # Green


class TPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [4, 20], [4, 21], [5, 20]]

    # TODO: this
    def _get_rotation_coords(self, order):
        pass

    @staticmethod
    def get_colour():
        return 221, 10, 178  # Purple


class LPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [4, 20], [5, 20], [5, 21]]

    # TODO: this
    def _get_rotation_coords(self, order):
        pass

    @staticmethod
    def get_colour():
        return 255, 200, 46  # Orange


class JPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [3, 21], [4, 20], [5, 20]]

    # TODO: this
    def _get_rotation_coords(self, order):
        pass

    @staticmethod
    def get_colour():
        return 0, 119, 211  # Blue


class OPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[4, 21], [4, 20], [5, 21], [5, 20]]

    # TODO: this
    def _get_rotation_coords(self, order):
        pass

    @staticmethod
    def get_colour():
        return 254, 251, 52  # Yellow


if __name__ == "__main__":
    playfield = Playfield()
    piece = IPiece(playfield)

    # MOVEMENT TEST
    print(piece.get_coordinates(), piece.get_corner_position())
    piece.drop()
    print(piece.get_coordinates(), piece.get_corner_position())
    piece.left()
    print(piece.get_coordinates(), piece.get_corner_position())
    piece.left()
    piece.left()
    piece.left()
    print(piece.get_coordinates(), piece.get_corner_position())
    piece.right()
    print(piece.get_coordinates(), piece.get_corner_position())
    piece.right()
    piece.right()
    piece.right()
    piece.right()
    piece.right()
    piece.right()
    print(piece.get_coordinates(), piece.get_corner_position())
    piece.rotate_right()
    piece.right()
    piece.right()
    piece.rotate_right()
    print(piece.get_coordinates(), piece.get_corner_position())

    piece.hard_drop()
    print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    X, Y = playfield.get_dimensions()
    for i_1 in range(Y):
        for j_1 in range(X):
            print(playfield.is_clear(j_1, Y - i_1 - 1), end="")
        print()

    # ROTATION TEST
    # playfield.add_blocks(((4, 18), ), (0, 0, 0))
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # piece.rotate_right()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # piece.rotate_right()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # piece.rotate_right()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # piece.rotate_left()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # piece.rotate_left()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # piece.rotate_left()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
