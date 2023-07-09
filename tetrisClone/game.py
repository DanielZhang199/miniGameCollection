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
MIN_PLACE_DELAY = 45  # Frames you get to move pieces after a rotation

MAX_ROTATES = 15
MAX_HOLDS = 2

pg.init()
pg.font.init()
FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE)
BIG_FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE + 10)
SMALL_FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE - 9)


# following classes for certain surfaces are tightly coupled to the game window, and are placed here for organization
class SurfaceField:
    """
    sprite representing the game field in tetris, not the data structure
    """
    def __init__(self, playfield: Playfield, cur_piece: tet.Piece):
        self.surface = pg.Surface(FIELD_SIZE)
        self._field = playfield  # reference to playfield object being used
        self._cur_piece = cur_piece  # reference to current piece object (should not ever be none)
        self._ghost_coords = self._cur_piece.get_ghost_coords()

    def set_cur_piece(self, cur_piece):
        self._cur_piece = cur_piece
        self._ghost_coords = self._cur_piece.get_ghost_coords()

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
            self._draw_rect_alpha(self._cur_piece.get_colour() + (GHOST_ALPHA,),
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


class SurfaceScore:
    """
    Class for score/high score UI element
    """

    def __init__(self):
        self.surface = pg.Surface(SCORE_SIZE)


class SurfaceHold:
    """
    Class for displaying held piece
    """

    def __init__(self):
        self.surface = pg.Surface(HOLD_SIZE)


class SurfaceNext:
    """
    Class for displaying next pieces
    """
    def __init__(self):
        self.surface = pg.Surface(NEXT_SIZE)


class SurfaceText:
    """
    Class for displaying text when line clears happen
    """

    def __init__(self):
        self.surface = pg.Surface(TEXT_BOX_SIZE)


class TetrisGame:
    """
    class for tetris game window
    Attributes:
        - display: pygame.surface
        - options: (dict) values for infinity, ghost, and max rotates
        - bag: (Bag) 7-bag piece generator
        - current: (Piece) current user controlled piece
        - field: (Playfield) current field state
    """
    def __init__(self, infinity=False, ghost=True, max_rotates=15, music=None):
        self.display = pg.display.set_mode(WINDOW_SIZE)
        self.display.fill(BG_COLOUR)
        pg.display.set_caption("Object Oriented Tetris")
        self._options = {"INFINITY": infinity, "GHOST": ghost, "MAX_ROTATES": max_rotates}
        if music is not None:  # I don't plan on writing a soundtrack, so only one song will play :D
            pg.mixer.music.load(music)
            pg.mixer.music.set_volume(VOLUME)
            pg.mixer.music.play(-1)

        self.bag = Bag()
        self.field = Playfield()
        self.current = tet.num_to_piece(self.bag.next())(self.field)
        self.held = None
        self.level = 1
        self.game_state = {"lines": self._lines_to_next(), "next_move": self._get_next_move(), "move_timer": 0,
                           "drop_timer": 0, "rotates_left": MAX_ROTATES, "combo_count": -1, "b2b": False, "holds": 0,
                           "last_action": "", "place_delay": 0}
        self._surface_field = SurfaceField(self.field, self.current)
        self._surface_score = SurfaceScore()
        self._surface_hold = SurfaceHold()
        self._surface_next = SurfaceNext()
        self._surface_text = SurfaceText()
        self.running = True
        self.start()

    def start(self):
        """
        starts a new tetris game
        :return: (nothing)
        """
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    self._handle_input(event.key)
            self._handle_held(pg.key.get_pressed())

            self.game_state["next_move"] -= 1
            if self.game_state["next_move"] <= 0:
                self.game_state["next_move"] = self._get_next_move()
                if not self.current.drop():
                    if self.game_state["place_delay"] <= 0:
                        self._place_piece()
                else:
                    self.game_state["last_action"] = "DOWN"

            # something to update fade out text
            self._update_field()
            # something to update score
            pg.display.flip()
            pg.time.Clock().tick(FPS)

    def _update_field(self):
        self._surface_field.update(self._options["GHOST"])
        self._surface_field.draw_ghost()
        self.display.blit(self._surface_field.surface, FIELD_COORDS)

    def _handle_input(self, key):
        match key:
            case pg.K_LEFT:
                self.game_state["move_timer"] = 0
                if self.current.left():
                    self._move_helper()
            case pg.K_RIGHT:
                self.game_state["move_timer"] = 0
                if self.current.right():
                    self._move_helper()
            case pg.K_DOWN:
                self.game_state["drop_timer"] = 0
                if self.current.drop():
                    self.game_state["last_action"] = "DOWN"
                    # score += SCORING_BASE_VALUES["SoftDrop"]
            case pg.K_SPACE:
                # score += SCORING_BASE_VALUES["HardDrop"] * cur_piece.hard_drop()
                self.current.hard_drop()
                self.game_state["last_action"] = "DOWN"
                self._place_piece()
            case pg.K_x | pg.K_UP:
                self.current.rotate_right()
                self._rotate_helper()
            case pg.K_z:
                self.current.rotate_left()
                self._rotate_helper()
            case pg.K_c:
                if not self.game_state["holds"] == MAX_HOLDS:
                    self.game_state["holds"] += 1
                    if self.held is None:
                        self.held = self.current
                        self._next_piece()
                    else:
                        self.held, self.current = self.current, self.held
                        self.current.__init__(self.field)
                        self._reset_current()
                    # update hold surface

    def _rotate_helper(self):
        """
        runs whenever a piece rotates, updates needed values after rotations
        """
        self.game_state["last_action"] = "ROTATE"
        self._surface_field.calculate_ghost()
        if self.game_state["rotates_left"] >= 0:
            self.game_state["place_delay"] = MIN_PLACE_DELAY
            if not self._options["INFINITY"]:
                self.game_state["rotates_left"] -= 1

    def _move_helper(self):
        """
        runs whenever a piece moves. updates needed values for movement
        """
        self._surface_field.calculate_ghost()
        self.game_state["last_action"] = 'SIDE'

    def _handle_held(self, keys):
        if keys[pg.K_LEFT] and keys[pg.K_RIGHT]:
            pass
        elif keys[pg.K_LEFT]:
            self.game_state["move_timer"] += 1
            if self.game_state["move_timer"] >= MOVE_DELAY:
                self.game_state["move_timer"] -= MOVE_REPEAT
                if self.current.left():
                    self._move_helper()
        elif keys[pg.K_RIGHT]:
            self.game_state["move_timer"] += 1
            if self.game_state["move_timer"] >= MOVE_DELAY:
                self.game_state["move_timer"] -= MOVE_REPEAT
                if self.current.right():
                    self._move_helper()
        if keys[pg.K_DOWN]:
            self.game_state["drop_timer"] += 1
            self.game_state["drop_timer"] -= SOFT_DROP_SPEED
            if self.game_state["drop_timer"] >= MOVE_DELAY:
                if self.current.drop():
                    # score += SCORING_BASE_VALUES["SoftDrop"]
                    self.game_state["last_action"] = "DOWN"

    def _get_next_move(self):
        # return either FPS - level * FPS // 10 (linear decrease from 1 second to 0 seconds over 15 levels)
        # or minimum of 1 frame
        return max(FPS - (self.level - 1) * FPS // 20, 1)

    def _lines_to_next(self):
        return 4 + self.level

    def _reset_current(self):
        """
        updates values whenever a new piece takes the field
        """
        self.game_state["rotates_left"] = MAX_ROTATES
        self.game_state["last_action"] = ""
        self.game_state["next_move"] = self._get_next_move()
        self._surface_field.set_cur_piece(self.current)

    def _next_piece(self):
        """
        gets the next piece
        """
        self.current = tet.num_to_piece(self.bag.next())(self.field)
        self._reset_current()

    def _place_piece(self):
        self.game_state["holds"] = 0  # only reset this when piece is placed
        is_t_spin = (type(self.current) == tet.TPiece and self.game_state["last_action"] == "ROTATE" and
                    self.current.t_spin_corners_satisfied())
        lines_cleared = self.current.place()
        if lines_cleared > 0:
            self.game_state["combo_count"] += 1
            if self.game_state["combo_count"] > 0:
                combo_bonus = SCORING_BASE_VALUES["Combo"] * self.level * self.game_state["combo_count"]
                # score += combo_bonus
                # current_text[1] = f"{combo_count} COMBO "
            else:
                combo_bonus = 0
                # current_text[1] = ""

            if lines_cleared == 4:
                if self.game_state["b2b"]:
                    increment = int(SCORING_BASE_VALUES[4] * self.level * BACK_TO_BACK_MULTIPLIER)
                    # the multiplier is a float
                    # score += increment
                    # current_text[0] = "TETRIS "
                    # current_text[1] = "B2B "
                    # current_text_alpha = 950
                else:
                    increment = SCORING_BASE_VALUES[4] * self.level
                    # score += increment
                    # current_text[0] = f"TETRIS"
                    # current_text_alpha = 860
                    self.game_state["b2b"] = True
            elif is_t_spin:
                if self.game_state["b2b"]:
                    increment = int(SCORING_BASE_VALUES["TSpin" + str(lines_cleared)] * self.level
                                    * BACK_TO_BACK_MULTIPLIER)
                    # score += increment
                    # current_text[0] = f"T-SPIN {NUMBER_TO_WORD[lines_cleared]}"
                    # current_text[1] = "B2B "
                    # current_text_alpha = 980
                else:
                    increment = SCORING_BASE_VALUES["TSpin" + str(lines_cleared)] * self.level
                    # score += increment
                    # current_text[0] = f"T-SPIN {NUMBER_TO_WORD[lines_cleared]}"
                    # current_text_alpha = 860
                    self.game_state["b2b"] = True
            else:
                self.game_state["b2b"] = False
                increment = SCORING_BASE_VALUES[lines_cleared] * self.level
                # score += increment
                # current_text[0] = f"{NUMBER_TO_WORD[lines_cleared]}"
                # current_text_alpha = 800

            # current_text[1] += f"(+ {increment + combo_bonus})"

            self.game_state["lines"] -= lines_cleared
            if self.game_state["lines"] <= 0:
                self.level += 1
                self.game_state["lines"] += self._lines_to_next()
        else:
            self.game_state["combo_count"] = -1

        if self.field.garbage_out():
            self.running = False
        self._next_piece()


if __name__ == "__main__":
    TetrisGame()
