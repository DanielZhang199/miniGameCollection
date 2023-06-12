from random import shuffle

PIECES = [i for i in range(7)]


class Bag:
    """
    Class to cycle through 7 numbers in a pseudo-random order. This is an implementation of the tetris 7-bag
    """
    def __init__(self):
        temp1 = PIECES.copy()
        shuffle(temp1)
        temp2 = PIECES.copy()
        shuffle(temp2)
        self._queue = temp1 + temp2

    def next(self):
        """
        returns the next piece (random), resets the state if all pieces were outputted already
        :return: one of the 7 tetromino objects
        """
        if len(self._queue) <= len(PIECES):
            temp = PIECES.copy()
            shuffle(temp)
            self._queue += temp
        return self._queue.pop(0)

    def show_next_n(self, n: int):
        """
        returns a tuple of the next n numbers
        :param n: integer from 1-7
        :return: (tuple) of integers representing the next n inputs
        """
        return tuple(self._queue[:n])


if __name__ == "__main__":
    test = Bag()
    for i in range(5):
        for j in range(14):
            print(test.next(), end=", ")
        print()
