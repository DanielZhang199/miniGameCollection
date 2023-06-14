from playfield import Playfield

DEFAULT_WALL_KICK_DATA = {"0>1": ((-1, 0), (-1, 1), (0, -2), (-1, -2)), "1>0": ((1, 0), (1, -1), (0, 2), (1, 2)),
                          "1>2": ((1, 0), (1, -1), (0, 2), (1, 2)), "2>1": ((-1, 0), (-1, 1), (0, -2), (-1, -2)),
                          "2>3": ((1, 0), (1, 1), (0, -2), (1, -2)), "3>2": ((-1, 0), (-1, -1), (0, 2), (-1, 2)),
                          "3>0": ((-1, 0), (-1, -1), (0, 2), (-1, 2)), "0>3": ((1, 0), (1, 1), (0, -2), (1, -2))}
I_WALL_KICK_DATA = {"0>1": ((-2, 0), (1, 0), (-2, -1), (1, 2)), "1>0": ((2, 0), (-1, 0), (2, 1), (-1, -2)),
                    "1>2": ((-1, 0), (2, 0), (-1, 2), (2, -1)), "2>1": ((1, 0), (-2, 0), (1, -2), (-2, 1)),
                    "2>3": ((2, 0), (-1, 0), (2, 1), (-1, -2)), "3>2": ((-2, 0), (1, 0), (-2, -1), (1, 2)),
                    "3>0": ((1, 0), (-2, 0), (1, -2), (-2, 1)), "0>3": ((-1, 0), (2, 0), (-1, 2), (2, -1))}


def num_to_piece(n: int):
    """
    turns the number given by the bag into a piece object class
    :param n: output from bag (integer between 0-6)
    :return: (type) type of piece
    """
    match n:
        case 0:
            return TPiece
        case 1:
            return IPiece
        case 2:
            return JPiece
        case 3:
            return LPiece
        case 4:
            return ZPiece
        case 5:
            return SPiece
        case 6:
            return OPiece


class Piece:
    """
    class for abstract piece class with shared functionality

    fields:
    - coordinates: (list) of 4 x, y coordinates for each of the piece components
    - corner: (list) position of top left corner of piece area (used for relative coordinates used for rotations)
    - rotation: (int) 0-3 current rotation state of piece
    - field: current playing field object
    - placed: (boolean) whether the piece has been placed (just so it cannot be placed twice due to bad code)
    """
    def __init__(self, pf: Playfield):
        if type(self) is Piece:
            raise Exception('Piece is an abstract class and cannot be instantiated directly')
        self._coordinates = None
        self._corner = [3, 21]  # x, y position of top left corner of 'hit-box' for rotations
        self._rotation = 0
        self._field = pf
        self._placed = False
        # all/most methods called on the piece will be with respect to the 'field', so it is also a field

    # GETTER METHODS:
    def get_corner_position(self):
        return self._corner

    def get_coordinates(self):
        return self._coordinates

    def _get_kicks(self, orientation):
        return DEFAULT_WALL_KICK_DATA[str(self._rotation) + ">" + str(orientation)]

    # abstract methods (not defied for generic piece)
    @staticmethod
    def get_colour():
        raise NotImplementedError("Subclass did not implement get_colour method")

    @staticmethod
    def default_piece_positions():
        raise NotImplementedError("Subclass did not implement default_piece_positions method")

    def _get_rotation_coords(self, order):
        raise NotImplementedError("Subclass did not implement _try_place method")

    # SETTER METHODS
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

    # in theory n will only be 1 or -1, but this still saves repeated code
    def _move(self, n):
        """
        moves piece n squares in positive or negative x direction (downwards would be a drop)
        :param n: (int) how much x position can be changed
        :return: nothing
        """
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0] + n, coord[1]):
                return
        for coord in self._coordinates:
            coord[0] += n
        self._corner[0] += n

    def drop(self):
        """
        drops the piece by one and returns true if the piece has space, if piece can no longer move, returns false
        :return: (boolean) true if piece was able to move
        """
        for coord in self._coordinates:
            if not self._field.is_clear(coord[0], coord[1] - 1):
                return False
        for coord in self._coordinates:
            coord[1] -= 1
        self._corner[1] -= 1
        return True

    def place(self):
        """
        if piece was not already placed down, places the piece and returns lines cleared, otherwise returns 0
        :return: (int) lines cleared from placing that piece
        """
        if not self._placed:
            self._placed = True
            return self._field.add_blocks(self._coordinates, self.get_colour())
        return 0  # return zero anyways

    def hard_drop(self):
        """
        calls drop over and over until it returns false. Not sure about the practicality, but this function is useful
        abstraction regardless of necessity
        :return: nothing (since we already know that the piece can't move further)
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
        self._perform_rotate(new_state)

    def rotate_left(self):
        """
        tries to rotate the piece right (using the SRS algorithm)
        :return: nothing
        """
        if self._rotation == 0:
            new_state = 3
        else:
            new_state = self._rotation - 1
        self._perform_rotate(new_state)

    # shared helper methods
    def _perform_rotate(self, orientation):
        """
        attempts to put the piece into specified rotation state/orientation, setting the rotation state to that value
        if the rotation attempt is successful. Rotation states are defined via the graphic (based on tetris guidelines)
        and kicks are attempted as needed according to those guidelines.
        :param orientation: (int) 0-3 orientation piece is attempting to rotation into
        :return: (nothing)
        """
        coords = self._get_rotation_coords(orientation)
        if self._try_set_coords(coords):
            # helper function above sets coordinates, we only need to change rotation value
            self._rotation = orientation
        else:
            kicks = self._get_kicks(orientation)
            for dx, dy in kicks:
                if self._try_set_coords([[x + dx, y + dy] for x, y in coords]):
                    self._rotation = orientation
                    self._corner[0] += dx
                    self._corner[1] += dy

    def _try_set_coords(self, coords):
        """
        attempts to set the current coordinates to be replaced by new specified coordinates, if all new coordinates are
        not in conflict with the current playing field, return true. Otherwise, do not change the coordinates and return
        false.
        :param coords: (list) of four sets of x, y coordinates
        :return: (boolean) whether function was successful
        """
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


# subclasses do not introduce new methods, and only implement or polymorph previously designed methods.
class IPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        # list of coordinates of each piece component when spawning
        self._coordinates = [[3, 20], [4, 20], [5, 20], [6, 20]]

    # while this seems like a static method, the absolute coordinates after rotation are dependent on piece position
    # in the playing field and therefore the function cannot be made completely static.
    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        match orientation:
            case 0:
                return self._abs_coords(((0, 1), (1, 1), (2, 1), (3, 1)))
            case 1:
                return self._abs_coords(((2, 0), (2, 1), (2, 2), (2, 3)))
            case 2:
                return self._abs_coords(((0, 2), (1, 2), (2, 2), (3, 2)))
            case 3:
                return self._abs_coords(((1, 0), (1, 1), (1, 2), (1, 3)))

    def _get_kicks(self, orientation):  # override for I piece
        return I_WALL_KICK_DATA[str(self._rotation) + ">" + str(orientation)]

    @staticmethod
    def get_colour():
        return 1, 237, 250  # Cyan

    # next method refers to relative coordinates of a piece in default rotation state. I.e. the line of coordinates of
    # _get_rotation_coords corresponding to case 0. Needed for drawing the piece when it is not in play.
    @staticmethod
    def default_piece_positions():
        return (0, 1), (1, 1), (2, 1), (3, 1)


class ZPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 21], [4, 21], [4, 20], [5, 20]]

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        match orientation:
            case 0:
                return self._abs_coords(((0, 0), (1, 0), (1, 1), (2, 1)))
            case 1:
                return self._abs_coords(((2, 0), (2, 1), (1, 1), (1, 2)))
            case 2:
                return self._abs_coords(((0, 1), (1, 2), (1, 1), (2, 2)))
            case 3:
                return self._abs_coords(((1, 0), (1, 1), (0, 1), (0, 2)))

    @staticmethod
    def get_colour():
        return 253, 63, 89  # Salmon

    @staticmethod
    def default_piece_positions():
        return (0, 0), (1, 0), (1, 1), (2, 1)


class SPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [4, 20], [4, 21], [5, 21]]

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        match orientation:
            case 0:
                return self._abs_coords(((0, 1), (1, 0), (1, 1), (2, 0)))
            case 1:
                return self._abs_coords(((2, 2), (2, 1), (1, 1), (1, 0)))
            case 2:
                return self._abs_coords(((0, 2), (1, 2), (1, 1), (2, 1)))
            case 3:
                return self._abs_coords(((0, 0), (1, 1), (0, 1), (1, 2)))

    @staticmethod
    def get_colour():
        return 83, 218, 63  # Green

    @staticmethod
    def default_piece_positions():
        return (0, 1), (1, 0), (1, 1), (2, 0)


class TPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [4, 20], [4, 21], [5, 20]]

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        match orientation:
            case 0:
                return self._abs_coords(((0, 1), (1, 0), (1, 1), (2, 1)))
            case 1:
                return self._abs_coords(((1, 2), (2, 1), (1, 1), (1, 0)))
            case 2:
                return self._abs_coords(((0, 1), (1, 2), (1, 1), (2, 1)))
            case 3:
                return self._abs_coords(((1, 0), (1, 1), (0, 1), (1, 2)))

    @staticmethod
    def get_colour():
        return 221, 10, 178  # Purple

    @staticmethod
    def default_piece_positions():
        return (0, 1), (1, 0), (1, 1), (2, 1)


class LPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [4, 20], [5, 20], [5, 21]]

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        match orientation:
            case 0:
                return self._abs_coords(((0, 1), (2, 0), (1, 1), (2, 1)))
            case 1:
                return self._abs_coords(((1, 2), (2, 2), (1, 1), (1, 0)))
            case 2:
                return self._abs_coords(((0, 1), (0, 2), (1, 1), (2, 1)))
            case 3:
                return self._abs_coords(((1, 0), (1, 1), (0, 0), (1, 2)))

    @staticmethod
    def get_colour():
        return 255, 200, 46  # Orange

    @staticmethod
    def default_piece_positions():
        return (0, 1), (2, 0), (1, 1), (2, 1)


class JPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[3, 20], [3, 21], [4, 20], [5, 20]]

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        match orientation:
            case 0:
                return self._abs_coords(((0, 1), (0, 0), (1, 1), (2, 1)))
            case 1:
                return self._abs_coords(((1, 2), (2, 0), (1, 1), (1, 0)))
            case 2:
                return self._abs_coords(((0, 1), (2, 2), (1, 1), (2, 1)))
            case 3:
                return self._abs_coords(((1, 0), (1, 1), (0, 2), (1, 2)))

    @staticmethod
    def get_colour():
        return 0, 119, 211  # Blue

    @staticmethod
    def default_piece_positions():
        return (0, 1), (0, 0), (1, 1), (2, 1)


class OPiece(Piece):
    def __init__(self, pf):
        super().__init__(pf)
        self._coordinates = [[4, 21], [4, 20], [5, 21], [5, 20]]

    def _get_rotation_coords(self, orientation):
        """
        gets the positions of pieces if tetromino was to rotate into specified position
        :param orientation: (int) rotation state, represented as an integer from 0-3
        :return: coords
        """
        return self._abs_coords(((1, 0), (2, 0), (1, 1), (2, 1)))

    def rotate_left(self):
        pass

    def rotate_right(self):
        pass

    @staticmethod
    def get_colour():
        return 254, 251, 52  # Yellow

    @staticmethod
    def default_piece_positions():
        return (1, 0), (2, 0), (1, 1), (2, 1)


if __name__ == "__main__":
    from tetrisClone.bag import Bag
    piece_bag = Bag()

    playfield = Playfield()
    for i in range(10):
        piece = num_to_piece(piece_bag.next())(playfield)
        print(piece.get_colour())
        print(type(piece))

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
    # print(piece.get_coordinates(), piece.get_corner_position())
    # piece.rotate_right()
    # piece.right()
    # piece.right()
    # piece.rotate_right()
    # print(piece.get_coordinates(), piece.get_corner_position())
    #
    # piece.hard_drop()
    # print(piece.get_coordinates(), piece.get_corner_position(), piece._rotation)
    # X, Y = playfield.get_dimensions()
    # for i_1 in range(Y):
    #     for j_1 in range(X):
    #         print(playfield.is_clear(j_1, Y - i_1 - 1), end="")
    #     print()

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
