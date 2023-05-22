GRAVITY = 1  # this is player acceleration by default
JUMP_STRENGTH = -20  # this is how fast you go after a jump
JUMP_TIMER = 5  # how many frames before next jump
TERMINAL_VELOCITY = 50
MAX_HEIGHT = 1360  # lowest the ball can go on the screen (player is 40 pixels in size)
MIN_HEIGHT = -80  # highest the ball can go on the screen


class Player:
    """
    Player class that can move up and down, has a position, and automatically falls unless given input
    """
    # EFFECTS: sets x and y positions to the specified location, and scales movement by a factor related to screen size
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self._dy = 0
        self.__cooldown = 0

    def jump(self):
        if self.__cooldown <= 0:
            self._dy = JUMP_STRENGTH
            self.__cooldown = JUMP_TIMER

    def tick(self):
        if self._dy < TERMINAL_VELOCITY:
            self._dy += GRAVITY
        self._y += self._dy
        if self._y > MAX_HEIGHT:
            self._y = MAX_HEIGHT

        elif self._y < MIN_HEIGHT:
            self._y = MIN_HEIGHT

        if self.__cooldown > 0:
            self.__cooldown -= 1

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y
