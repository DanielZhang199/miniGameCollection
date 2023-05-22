WIDTH = 10
HEIGHT = 22
# top 2 rows are invisible and not rendered
# game ends as soon as piece lands and has blocks above 20th row (i.e. off screen)


class Playfield:
    """
    class representing the current screen of pieces/map of tetris game
    """
    def __init__(self):
        """
        creates a 2d array of WIDTH rows with HEIGHT columns, coordinate on the board is grid[x][y]
        """
        self._grid = [[None for _ in range(HEIGHT)] for _ in range(WIDTH)]

    # TODO: implement this
    def add_blocks(self, coords, colour):
        """
        adds pieces to board grid and removes row if necessary
        :param coords: array of coordinates (list) or (tuple)
        :param colour: (list) or (tuple); r, g, b values
        :return: nothing
        """
        for x, y in coords:
            self._grid[x][y] = colour

    def get_contents(self, x: int, y: int):
        """
        returns tuple of colour of piece in x, y coordinate, or None
        :param x: between 0 to WIDTH - 1
        :param y: between 0 to HEIGHT - 1
        :return: (r, g, b) or None
        """
        return self._grid[x][y]

    def is_clear(self, x: int, y: int):
        """
        returns true if there is an empty space at requested x, y position, false if it is occupied our out of bounds
        :param x:
        :param y:
        :return:
        """
        if 0 <= x <= 9 and 0 <= y <= 21:
            return self._grid[x][y] is None
        return False


if __name__ == "__main__":
    testBoard = Playfield()
    for i in range(HEIGHT):
        for j in range(WIDTH):
            print(testBoard.is_clear(j, i), end="")
        print()
