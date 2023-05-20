import random

SCROLL_SPEED = 10  # how fast the obstacles move
SCREEN_HEIGHT = 1440
SCREEN_WIDTH = 2560
WIDTH = 140  # obstacle width
SPACING = 150  # double this value is how wide the opening is in pixels
PLAYER_SIZE = 80


class Obstacle:
    """
    Obstacle has a bounding box composed of 2 rectangles, and moves from right to left, opening location is random
    position that is 160 pixels from the top or bottom
    """
    def __init__(self):
        self._center = random.randint(160, (SCREEN_HEIGHT - 160))
        self._x = SCREEN_WIDTH
        self._cleared = False

    def tick(self, pos: tuple):
        """
        updates position and returns 1 if player is colliding, 2 if player cleared obstacle, 0 otherwise.
        :param pos: (tuple); (x, y) of player
        :return: (int) 0 means nothing
        """
        # update position
        self._x -= SCROLL_SPEED

        # check for collision
        if not self._cleared:
            player_x, player_y = pos[0], pos[1]
            if self._x - PLAYER_SIZE < player_x < self._x + WIDTH:
                if player_y < self._center - SPACING or player_y + PLAYER_SIZE > self._center + SPACING:
                    return 1
            elif player_x > self._x + WIDTH:
                self._cleared = True
                return 2
        return 0

    def get_dimensions(self):
        """
        returns 2 tuples, with the x, y, width and height of each component rectangle
        :return: (tuple); 2d array of points described
        """
        top = (self._x, 0, WIDTH, self._center - SPACING)
        bottom = (self._x, self._center + SPACING, WIDTH, SCREEN_HEIGHT)
        return top, bottom

