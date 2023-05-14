GRAVITY = 0.5  # this is player acceleration by default
JUMP_STRENGTH = -10  # this is how fast you go after a jump
JUMP_TIMER = 5  # how many frames before next jump
TERMINAL_VELOCITY = 25

class Player:
    """
    Player class that can move up and down, has a position, and automatically falls unless given input
    """
    # EFFECTS: sets x and y positions to the specified location, and scales movement by a factor related to screen size
    def __init__(self, x: int, y: int, scale: float):
        self._x = x * scale
        self._y = y * scale
        self._dy = 0
        self.__SCALING = scale
        self.__cooldown = 0

    def jump(self):
        if self.__cooldown <= 0:
            self._dy = JUMP_STRENGTH * self.__SCALING
            self.__cooldown = JUMP_TIMER
        else:
            print("FAILED JUMP")

    def tick(self):
        self._y += self._dy
        if self._dy < TERMINAL_VELOCITY:
            self._dy += GRAVITY * self.__SCALING
        if self.__cooldown > 0:
            self.__cooldown -= 1

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y


