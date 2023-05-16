WIDTH = 10
HEIGHT = 30


class Board:
    def __init__(self):
        """
        creates a 2d array of WIDTH rows with HEIGHT columns, coordinate on the board is grid[x][y]
        """
        self._grid = [["" for _ in range(HEIGHT)] for _ in range(WIDTH)]

    def add_pieces(self, pieces: list, colour: tuple):
        """
        adds pieces to board grid and removes row if necessary
        :param pieces: list of (x, y) coordinates
        :param colour: RGB color of pieces
        :return: nothing
        """
        pass

    def has_piece(self, x: int, y: int):
        """
        returns true if there is a piece already in the column and row on the board
        :param x: between 0 to WIDTH - 1
        :param y: between 0 to HEIGHT - 1
        :return: (boolean)
        """
        return False

    def get_board(self):
        return self._grid.copy()


if __name__ == "__main__":
    testBoard = Board()
    print(testBoard.get_board())
