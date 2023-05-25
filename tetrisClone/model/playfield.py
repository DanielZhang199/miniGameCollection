WIDTH = 10
HEIGHT = 24
# top 4 rows are invisible and not rendered
# game ends as soon as piece lands and has blocks above 20th row (i.e. off screen). We need 4 extra rows so the code
# doesn't crash if you place an I-piece on a block in row 20


class Playfield:
    """
    class representing the current screen of pieces/map of tetris game
    """
    def __init__(self):
        """
        creates a 2d array of HEIGHT rows with WIDTH columns, coordinate on the board is grid[y][x]
        """
        self._grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # TODO: implement this
    def add_blocks(self, coords, colour):
        """
        adds pieces to board grid and removes row if necessary. Returns number of rows cleared
        :param coords: array of coordinates list or tuple: (x, y)
        :param colour: list or tuple; (r, g, b) values
        :return: (int) number of rows cleared
        """
        # using naive line drop gravity logic (https://tetris.fandom.com/wiki/Line_clear#Line_clear_gravity)
        modified_rows = set()
        for x, y in coords:
            self._grid[y][x] = colour
            modified_rows.add(y)

        # clear lines top to bottom to ensure the lines being cleared don't move whilst clearing lines
        score = 0
        for y in modified_rows:
            if self._check_row(y):
                del self._grid[y]
                self._grid.append([None for _ in range(WIDTH)])
                score += 1

        return score

    def garbage_out(self):
        """
        returns true if there is a piece above row 20 (i.e. oob). Call this method after adding blocks
        keep in mind row 20 is index 19, as row index starts from 0.
        :return: (boolean)
        """
        # theoretically, there can't be anything above row 21 if row 21 is empty due to how pieces work
        for element in self._grid[20]:
            if element is not None:
                return True
        return False

    def get_contents(self, x: int, y: int):
        """
        returns tuple of colour of piece in x, y coordinate, or None, will raise exception if out of bounds
        :param x: between 0 to WIDTH - 1
        :param y: between 0 to HEIGHT - 1
        :return: (r, g, b) or None
        """
        return self._grid[y][x]

    def is_clear(self, x: int, y: int):
        """
        returns true if there is an empty space at requested x, y position, false if it is occupied or out of bounds
        :param x: (int)
        :param y: (int)
        :return: (boolean)
        """
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return self._grid[y][x] is None
        return False

    def _check_row(self, n):
        """
        returns true if row n is completely filled
        :param n: (int) row number, between 0 to HEIGHT - 1
        :return: (boolean)
        """
        for element in self._grid[n]:
            if element is None:
                return False
        return True

    @staticmethod
    def get_dimensions():
        return WIDTH, HEIGHT


if __name__ == "__main__":
    def print_field():
        print("\nPRINTING FIELD:")
        print("=" * 10)
        for i in range(HEIGHT):
            for j in range(WIDTH):
                print(str(testBoard.is_clear(j, HEIGHT - i - 1))[0], end="")
            print()
        print("=" * 10)

    testBoard = Playfield()
    testBoard.add_blocks([(x, 0) for x in range(9)] + [(x, 2) for x in range(9)] +
                         [(2, 1), (4, 1), (2, 3), (3, 4), (2, 4)], (1, 1, 1))
    print_field()
    print("Score = " + str(testBoard.add_blocks([(9, 0), (9, 1), (9, 2), (9, 3)], (0, 0, 0))))
    print_field()
