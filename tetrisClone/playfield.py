WIDTH = 10
HEIGHT = 22
# top 2 rows are invisible and not rendered
# game ends as soon as piece lands and has blocks above 20th row (i.e. off screen).


class Playfield:
    """
    class representing the current screen of pieces/map of tetris game
    """
    def __init__(self):
        """
        creates a 2d array of HEIGHT rows with WIDTH columns, coordinate on the board is grid[y][x]
        """
        self._grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

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
            try:
                self._grid[y][x] = colour
                modified_rows.add(y)
            except IndexError:
                pass

        # clear lines top to bottom to ensure the lines being cleared don't move whilst clearing lines
        score = 0
        while modified_rows:
            y = max(modified_rows)
            if self._check_row(y):
                del self._grid[y]
                self._grid.append([None for _ in range(WIDTH)])
                score += 1
            modified_rows.remove(y)

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
