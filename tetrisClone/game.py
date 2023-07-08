import pygame as pg
from bag import Bag
from playfield import Playfield
import tetrominoes as tet

WINDOW_SIZE = 930, 840
FPS = 60  # should be multiple of 30 (but other speeds should work)
SQUARE_SIZE = 40
FIELD_COORDS = 250, 20
FIELD_SIZE = SQUARE_SIZE * 10, SQUARE_SIZE * 20  # currently 400 by 800
GRID_DIMENSIONS = Playfield.get_dimensions()
GRID_WIDTH = 4
FONT_SIZE = 45

NEXT_SIZE = 190, 480
NEXT_COORDS = 705, 20
HSCORE_SIZE = 230, 100
HSCORE_COORDS = 675, 520
SCORE_SIZE = 230, 180
SCORE_COORDS = 675, 640

HOLD_SIZE = 190, 140
HOLD_COORDS = 30, 20
TEXT_BOX_SIZE = 250, 200
TEXT_LOCATION = 0, 200

MARGIN = 15
TEXT_COLOUR = (255,) * 3

BG_COLOUR = (95,) * 3
GRID_COLOUR = (30,) * 3
EMPTY_COLOUR = (10,) * 3

VOLUME = 0.1
SCORING_BASE_VALUES = {1: 100, 2: 300, 3: 500, 4: 800, "SoftDrop": 1, "HardDrop": 2, "Combo": 50,
                       "TSpin1": 800, "TSpin2": 1200, "TSpin3": 1600}  # zero line t-spin not implemented
NUMBER_TO_WORD = {1: "SINGLE", 2: "DOUBLE", 3: "TRIPLE"}
BACK_TO_BACK_MULTIPLIER = 1.5   # for tetris and t spins

GHOST_ALPHA = 50  # transparency for ghost pieces if enabled

# Define movement constants
MOVE_DELAY = 10  # Frames between continuous movements
MOVE_REPEAT = 3  # Frames between subsequent continuous movements
SOFT_DROP_SPEED = 2  # Frames between subsequent drops in a soft drop
MIN_PLACE_DELAY = 45

MAX_ROTATES = 15

pg.init()
pg.font.init()
FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE)
BIG_FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE + 10)
SMALL_FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE - 9)


class SurfaceField:
    """
    sprite representing the game field in tetris, not the data structure
    """
    def __init__(self, playfield: Playfield, cur_piece: tet.Piece):
        self.surface = pg.Surface(FIELD_SIZE)
        self._field = playfield  # reference to playfield object being used
        self._cur_piece = cur_piece  # reference to current piece object (can/should be changed over time)
        self._ghost_coords = []

    def update(self, ghost):
        """
        clears and redraws the field, current piece, and the grid (but not the ghost)
        im sure there's a way to make this more optimized, but it probably doesn't matter on most computers
        :return:
        """
        self.surface.fill(EMPTY_COLOUR)
        self._draw_field()
        if ghost:
            self.draw_ghost()
        self._draw_piece(self._cur_piece)
        self._draw_grid()

    def calculate_ghost(self):
        """
        calculates where the ghost piece parts should be
        :return:
        """
        self._ghost_coords = self._cur_piece.get_ghost_coords()

    def draw_ghost(self):
        for x, y in self._ghost_coords:
            x = x * SQUARE_SIZE
            y = FIELD_SIZE[1] - (y + 1) * SQUARE_SIZE
            self._draw_rect_alpha(self._cur_piece.get_colour() + (GHOST_ALPHA, ),
                                  pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))

    def _draw_rect_alpha(self, colour, rect):
        shape_surf = pg.Surface(pg.Rect(rect).size, pg.SRCALPHA)
        pg.draw.rect(shape_surf, colour, shape_surf.get_rect())
        self.surface.blit(shape_surf, rect)

    def _draw_field(self):
        width, height = GRID_DIMENSIONS
        for i in range(height):
            for j in range(width):
                contents = self._field.get_contents(j, height - i - 1)
                if contents is not None:
                    self._draw_block(j, height - i - 1, contents)

    def _draw_block(self, x, y, colour):
        x = x * SQUARE_SIZE
        y = FIELD_SIZE[1] - (y + 1) * SQUARE_SIZE
        pg.draw.rect(self.surface, colour, pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))

    def _draw_piece(self, piece):
        coords = piece.get_coordinates()
        colour = piece.get_colour()
        for x, y in coords:
            x = x * SQUARE_SIZE
            y = FIELD_SIZE[1] - (y + 1) * SQUARE_SIZE
            pg.draw.rect(self.surface, colour, pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))

    def _draw_grid(self):
        for x in range(GRID_DIMENSIONS[0]):
            x *= SQUARE_SIZE
            pg.draw.line(self.surface, GRID_COLOUR, (x, 0), (x, FIELD_SIZE[1]), GRID_WIDTH)

        for y in range(GRID_DIMENSIONS[1]):
            y *= SQUARE_SIZE
            pg.draw.line(self.surface, GRID_COLOUR, (0, y), (FIELD_SIZE[0], y), GRID_WIDTH)


class TetrisGame:
    """
    class for tetris game window
    Attributes:
        - display: pygame.surface
        - options: (dict) values for infinity, ghost, and max rotates
        - bag: (Bag) 7-bag piece generator
        - current: (Piece) current user controlled piece
        - field: (Playfield) current field state
        - surface_field: (Field), the UI element, not the data model
    """
    def __init__(self, infinity=False, ghost=True, max_rotates=15, music=None):
        self._display = pg.display.set_mode(WINDOW_SIZE)
        self._display.fill(BG_COLOUR)
        pg.display.set_caption("Object Oriented Tetris")
        self._options = {"INFINITY": infinity, "GHOST": ghost, "MAX_ROTATES": max_rotates}
        if music is not None:  # I don't plan on writing a soundtrack, so only one song will play :D
            pg.mixer.music.load(music)
            pg.mixer.music.set_volume(VOLUME)
            pg.mixer.music.play(-1)

        self._bag = None
        self._field = None
        self._current = None
        self._surface_field = None
        self.start()

    def start(self):
        """
        starts a new tetris game
        :return: (nothing)
        """
        self._bag = Bag()
        self._field = Playfield()
        self._current = tet.num_to_piece(self._bag.next())(self._field)
        self._surface_field = SurfaceField(self._field, self._current)
        self._surface_field.calculate_ghost()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self._current.drop()
            self._surface_field.update(self._options["GHOST"])
            self._surface_field.draw_ghost()
            self._display.blit(self._surface_field.surface, FIELD_COORDS)
            pg.display.flip()
            pg.time.Clock().tick(1)


if __name__ == "__main__":
    TetrisGame()