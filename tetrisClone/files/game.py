import pygame as pg
from files.bag import Bag
from files.playfield import Playfield
import files.tetrominoes as tet

WINDOW_SIZE = 930, 840
FPS = 60  # should be multiple of 30 (but other speeds should work)

GRID_WIDTH = 4
SQUARE_SIZE = 40
FIELD_COORDS = 250, 20
FIELD_SIZE = SQUARE_SIZE * 10, SQUARE_SIZE * 20  # currently 400 by 800
GRID_DIMENSIONS = Playfield.get_dimensions()

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
                       "TSpin0": 400, "TSpin1": 800, "TSpin2": 1200, "TSpin3": 1600}
NUMBER_TO_WORD = {1: "SINGLE", 2: "DOUBLE", 3: "TRIPLE"}
BACK_TO_BACK_MULTIPLIER = 1.5  # for tetris and t spins

GHOST_ALPHA = 50  # transparency for ghost pieces if enabled

pg.init()
pg.font.init()
FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE)
BIG_FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE + 10)
SMALL_FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE - 9)


def get_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        with open("high_score.txt", "w") as f:
            f.write("0")
            return 0


def write_high_score(num):
    if num > get_high_score():
        with open("high_score.txt", "w") as f:
            f.write(str(num))


# following classes for certain surfaces are tightly coupled to the game window, and are placed here for organization
class SurfaceField:
    """
    sprite representing the game field in tetris, not the data structure
    """

    def __init__(self, playfield: Playfield, cur_piece: tet.Piece):
        self.surface = pg.Surface([FIELD_SIZE[0] + GRID_WIDTH // 2, FIELD_SIZE[1] + GRID_WIDTH // 2])
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
        self._draw_piece(self._cur_piece)
        self._draw_grid()
        if ghost:
            self._draw_ghost()

    def calculate_ghost(self):
        """
        calculates where the ghost piece parts should be
        :return:
        """
        self._ghost_coords = self._cur_piece.get_ghost_coords()

    def _draw_ghost(self):
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
        for x in range(GRID_DIMENSIONS[0] + 1):
            x *= SQUARE_SIZE
            pg.draw.line(self.surface, GRID_COLOUR, (x, 0), (x, FIELD_SIZE[1]), GRID_WIDTH)

        for y in range(GRID_DIMENSIONS[1] + 1):
            y *= SQUARE_SIZE
            pg.draw.line(self.surface, GRID_COLOUR, (0, y), (FIELD_SIZE[0] + GRID_WIDTH, y), GRID_WIDTH)


class SurfaceScore:
    """
    Class for score/level UI element
    """
    static_text_1 = FONT.render("SCORE:", True, TEXT_COLOUR)
    static_text_2 = FONT.render("LEVEL:", True, TEXT_COLOUR)

    def __init__(self):
        self.surface = pg.Surface(SCORE_SIZE)
        self.score = 0
        self.level = 1
        self._render()

    def update(self, score, level_up=False):
        """
        adds score to the current score, and updates the score display
        if level_up, then increment level by one
        :param score: (int)
        :param level_up: (bool)
        :return: (nothing)
        """
        self.score += score
        if level_up:
            self.level += 1
        self._render()

    def _render(self):
        self.surface.fill(GRID_COLOUR)
        score_text = FONT.render(str(self.score), True, TEXT_COLOUR)
        level_text = FONT.render(str(self.level), True, TEXT_COLOUR)
        score_x_pos = SCORE_SIZE[0] - score_text.get_rect().width - MARGIN
        level_x_pos = SCORE_SIZE[0] - level_text.get_rect().width - MARGIN
        self.surface.blit(self.static_text_1, (15, MARGIN))
        self.surface.blit(score_text, (score_x_pos, FONT_SIZE + MARGIN))
        self.surface.blit(level_text, (level_x_pos, FONT_SIZE * 2 + MARGIN * 3))
        self.surface.blit(self.static_text_2, (15, FONT_SIZE * 2 + MARGIN * 3))


class SurfaceHold:
    """
    Class for displaying held piece
    """
    static_text = FONT.render("HOLD:", True, TEXT_COLOUR)
    text_pos = (45, MARGIN)

    def __init__(self, size=HOLD_SIZE):
        self.surface = pg.Surface(size)
        self.surface.fill(GRID_COLOUR)
        self.surface.blit(self.static_text, self.text_pos)

    def update(self, held: tet.Piece):
        """
        takes in a piece as input, and displays that piece on the surface
        :param held: currently held tetris piece
        :return: (nothing)
        """
        self._clear()
        if type(held) == tet.IPiece or type(held) == tet.OPiece:
            offset = (HOLD_SIZE[0] // 7, HOLD_SIZE[1] // 9)
        else:
            offset = (HOLD_SIZE[0] // 4, HOLD_SIZE[1] // 9)
        self._draw_graphic_on(held.get_colour(), SQUARE_SIZE // 1.2, held.default_piece_positions(), offset, 2)

    def _clear(self):
        self.surface.fill(GRID_COLOUR)
        self.surface.blit(self.static_text, self.text_pos)

    def _draw_graphic_on(self, colour, size, coords, offset, border):
        for x, y in coords:
            x = x * size + offset[0]
            y = y * size + FONT_SIZE + offset[1]
            if border > 0:
                pg.draw.rect(self.surface, (0, 0, 0), pg.Rect(x, y, size, size))
            pg.draw.rect(self.surface, colour, pg.Rect(x + border, y + border, size - border * 2, size - border * 2))


class SurfaceNext(SurfaceHold):
    """
    Class for displaying next pieces
    """
    static_text = FONT.render("NEXT:", True, TEXT_COLOUR)
    text_pos = (50, MARGIN)

    def __init__(self, bag, size=NEXT_SIZE):
        super().__init__(size)
        self._bag = bag
        self.update()

    def update(self, _=None):
        """
        method violates Liskov substitution principle; displays the next 5 pieces in the bag onto surface
        :param _: method must accept a parameter due to inheritance
        :return: (nothing)
        """
        self._clear()
        next_pieces = self._bag.show_next_n(5)
        for i, piece_num in enumerate(next_pieces):
            p_type = tet.num_to_piece(piece_num)
            if p_type == tet.IPiece:
                offset = (NEXT_SIZE[0] // 5, NEXT_SIZE[1] // 5.7 * i + 5)
            elif p_type == tet.OPiece:
                offset = (NEXT_SIZE[0] // 5, NEXT_SIZE[1] // 5.7 * i + 15)
            else:
                offset = (NEXT_SIZE[0] // 3.5, NEXT_SIZE[1] // 5.7 * i + 15)
            self._draw_graphic_on(p_type.get_colour(), SQUARE_SIZE // 1.2, p_type.default_piece_positions(), offset, 2)


class SurfaceText:
    """
    Class for displaying text when line clears happen
    """
    FADE_RATE = 10

    def __init__(self):
        self.surface = pg.Surface(TEXT_BOX_SIZE)
        self.surface.fill(BG_COLOUR)
        self.text1 = "PLACEHOLDER"
        self.text2 = "TEXT"
        self.alpha = 0

    def write(self, text1, text2, alpha):
        """
        sets the main text and subtext and alpha values
        :param text1: (str) large text to be shown on top
        :param text2: (str) small text to display score or combo info
        :param alpha: (int) positive integer to represent how long to display/how transparent the text is
        :return: (nothing)
        """
        self.text1 = text1
        self.text2 = text2
        self.alpha = alpha
        self.update()

    def update(self):
        """
        renders the text onto surface and lowers the transparency
        :return: (nothing)
        """
        self.surface.fill(BG_COLOUR)
        text1 = BIG_FONT.render(self.text1, True, TEXT_COLOUR)
        if text1.get_rect().width > 250:
            text1 = FONT.render(self.text1, True, TEXT_COLOUR)
        text1.set_alpha(self.alpha)
        text2 = SMALL_FONT.render(self.text2, True, TEXT_COLOUR)
        text2.set_alpha(self.alpha)

        line1_x_pos = TEXT_BOX_SIZE[0] - text1.get_rect().width - MARGIN
        line2_x_pos = TEXT_BOX_SIZE[0] - text2.get_rect().width - MARGIN

        self.surface.blit(text1, (line1_x_pos, MARGIN))
        self.surface.blit(text2, (line2_x_pos, FONT_SIZE + MARGIN))
        self.alpha -= self.FADE_RATE


class TetrisGame:
    """
    class for tetris game window; instantiating object will run an instance of the game
    """
    # Define movement constants
    MOVE_DELAY = 10  # Frames between continuous movements
    MOVE_REPEAT = 3  # Frames between subsequent continuous movements
    SOFT_DROP_SPEED = 2  # Frames between subsequent drops in a soft drop
    MIN_PLACE_DELAY = 30  # Frames you get to move pieces after a rotation or drop
    MAX_HOLDS = 2

    def __init__(self, infinity=False, ghost=True, max_rotates=15, music=None):
        self.display = pg.display.set_mode(WINDOW_SIZE)
        self.display.fill(BG_COLOUR)
        pg.display.set_caption("Tetris 2.1")
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
                           "drop_timer": 0, "rotates_left": max_rotates, "combo_count": -1, "b2b": False,
                           "holds": 0, "place_delay": 0}
        self._surface_field = SurfaceField(self.field, self.current)
        self.display.blit(self._surface_field.surface, FIELD_COORDS)
        self._surface_score = SurfaceScore()
        self.display.blit(self._surface_score.surface, SCORE_COORDS)
        self._surface_hold = SurfaceHold()
        self.display.blit(self._surface_hold.surface, HOLD_COORDS)
        self._surface_next = SurfaceNext(self.bag)
        self.display.blit(self._surface_next.surface, NEXT_COORDS)
        self._surface_text = SurfaceText()
        self.running = True
        self.over = False
        self._start()

    def _start(self):
        self.render_hs()

        while self.running and not self.over:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    self._handle_input(event.key)
            self._handle_held(pg.key.get_pressed())

            self.game_state["next_move"] -= 1
            self.game_state["place_delay"] -= 1
            if self.game_state["next_move"] <= 0:
                self.game_state["next_move"] = self._get_next_move()
                if not self.current.drop():
                    if self.game_state["place_delay"] <= 0:
                        self._place_piece()

            self._update_field()

            if self._surface_text.alpha > -10:
                self._surface_text.update()
                self.display.blit(self._surface_text.surface, TEXT_LOCATION)

            pg.display.flip()
            pg.time.Clock().tick(FPS)

        write_high_score(self._surface_score.score)
        if self.over and self.running:
            self.pause(text="GAME OVER")
            self.restart()

    def restart(self):
        self.bag = Bag()
        self.field = Playfield()
        self.current = tet.num_to_piece(self.bag.next())(self.field)
        self.held = None
        self.level = 1
        self.game_state = {"lines": self._lines_to_next(), "next_move": self._get_next_move(), "move_timer": 0,
                           "drop_timer": 0, "rotates_left": self._options["MAX_ROTATES"], "combo_count": -1,
                           "b2b": False, "holds": 0, "place_delay": 0}
        self._surface_field = SurfaceField(self.field, self.current)
        self.display.blit(self._surface_field.surface, FIELD_COORDS)
        self._surface_score = SurfaceScore()
        self.display.blit(self._surface_score.surface, SCORE_COORDS)
        self._surface_hold = SurfaceHold()
        self.display.blit(self._surface_hold.surface, HOLD_COORDS)
        self._surface_next = SurfaceNext(self.bag)
        self.display.blit(self._surface_next.surface, NEXT_COORDS)
        self._surface_text = SurfaceText()
        self.over = False
        self._start()

    def _update_field(self):
        self._surface_field.update(self._options["GHOST"])
        self.display.blit(self._surface_field.surface, FIELD_COORDS)

    def _increment_score(self, val, level_up=False):
        self._surface_score.update(val, level_up)
        self.display.blit(self._surface_score.surface, SCORE_COORDS)

    def _handle_input(self, key):
        match key:
            case pg.K_ESCAPE:
                self.pause()
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
                    self._drop_helper()
            case pg.K_SPACE:
                self._increment_score(SCORING_BASE_VALUES["HardDrop"] * self.current.hard_drop())
                self._place_piece()
            case pg.K_x | pg.K_UP:
                self.current.rotate_right()
                self._rotate_helper()
            case pg.K_z:
                self.current.rotate_left()
                self._rotate_helper()
            case pg.K_c:
                if self.game_state["holds"] < self.MAX_HOLDS:
                    self._handle_hold()

    def _handle_hold(self):
        self.game_state["holds"] += 1
        if self.held is None:
            self.held = self.current
            self._next_piece()
        else:
            self.held, self.current = self.current, self.held
            self.current.__init__(self.field)
            self._reset_current()
        self._surface_hold.update(self.held)
        self.display.blit(self._surface_hold.surface, HOLD_COORDS)

    def _rotate_helper(self):
        """
        runs whenever a piece rotates, updates needed values after rotations
        """
        self._surface_field.calculate_ghost()
        if self.game_state["rotates_left"] >= 0:
            self.game_state["place_delay"] = self.MIN_PLACE_DELAY
            if not self._options["INFINITY"]:
                self.game_state["rotates_left"] -= 1

    def _move_helper(self):
        """
        runs whenever a piece moves. updates needed values for movement
        """
        self._surface_field.calculate_ghost()

    def _drop_helper(self):
        self._increment_score(SCORING_BASE_VALUES["SoftDrop"])
        self.game_state["place_delay"] = self.MIN_PLACE_DELAY

    def _handle_held(self, keys):
        if keys[pg.K_LEFT] and keys[pg.K_RIGHT]:
            pass
        elif keys[pg.K_LEFT]:
            self.game_state["move_timer"] += 1
            if self.game_state["move_timer"] >= self.MOVE_DELAY:
                self.game_state["move_timer"] -= self.MOVE_REPEAT
                if self.current.left():
                    self._move_helper()
        elif keys[pg.K_RIGHT]:
            self.game_state["move_timer"] += 1
            if self.game_state["move_timer"] >= self.MOVE_DELAY:
                self.game_state["move_timer"] -= self.MOVE_REPEAT
                if self.current.right():
                    self._move_helper()
        if keys[pg.K_DOWN]:
            self.game_state["drop_timer"] += 1
            if self.game_state["drop_timer"] >= self.MOVE_DELAY:
                self.game_state["drop_timer"] -= self.SOFT_DROP_SPEED
                if self.current.drop():
                    self._drop_helper()

    def _get_next_move(self):
        # return either FPS - level * FPS // 10 (linear decrease from 1 second to 0 seconds over 15 levels)
        # or minimum of 1 frame (at 60 fps, this would drop the entire board length in 1/3 seconds)
        return max(FPS - (self.level - 1) * FPS // 20, 1)

    def _lines_to_next(self):
        return 4 + self.level

    def _reset_current(self):
        """
        updates values whenever a new piece takes the field
        """
        self.game_state["rotates_left"] = self._options["MAX_ROTATES"]
        self.game_state["next_move"] = self._get_next_move()
        self._surface_field.set_cur_piece(self.current)
        self._surface_next.update()
        self.display.blit(self._surface_next.surface, NEXT_COORDS)

    def _next_piece(self):
        """
        gets the next piece
        """
        self.current = tet.num_to_piece(self.bag.next())(self.field)
        self._reset_current()

    def _place_piece(self):
        self.game_state["holds"] = 0  # only reset this when piece is placed

        # placing a piece also clears lines, need to test t-spin before clearing/checking if lines will be cleared
        is_t_spin = (type(self.current) == tet.TPiece and self.current.get_last_action() == "ROTATE" and
                     self.current.t_spin_corners_satisfied())
        lines_cleared = self.current.place()
        if lines_cleared > 0:
            self.game_state["combo_count"] += 1
            self._handle_scoring(lines_cleared, is_t_spin)
        else:
            self.game_state["combo_count"] = -1
            if is_t_spin:
                score_increase = SCORING_BASE_VALUES["TSpin0"]
                self._surface_text.write("T-SPIN", f"(+ {score_increase})", 800)
                self._increment_score(score_increase, False)

        if self.field.garbage_out():
            self.over = True
        self._next_piece()

    def _handle_scoring(self, lines, is_t_spin):
        score_increase = 0
        level_up = False
        if self.game_state["combo_count"] > 0:
            combo_bonus = SCORING_BASE_VALUES["Combo"] * self.level * self.game_state["combo_count"]
            score_increase += combo_bonus
            text2 = f"{self.game_state['combo_count']} COMBO "
        else:
            text2 = ""

        if lines == 4:
            if self.game_state["b2b"]:
                # multiplier is a float
                score_increase += int(SCORING_BASE_VALUES[4] * self.level * BACK_TO_BACK_MULTIPLIER)
                text1 = "TETRIS "
                text2 = "B2B "
                text_alpha = 950
            else:
                score_increase += SCORING_BASE_VALUES[4] * self.level
                text1 = f"TETRIS"
                text_alpha = 860
                self.game_state["b2b"] = True
        elif is_t_spin:
            if self.game_state["b2b"]:
                pass
                score_increase += int(SCORING_BASE_VALUES["TSpin" + str(lines)] * self.level * BACK_TO_BACK_MULTIPLIER)
                text1 = f"T-SPIN {NUMBER_TO_WORD[lines]}"
                text2 = "B2B "
                text_alpha = 980
            else:
                score_increase += SCORING_BASE_VALUES["TSpin" + str(lines)] * self.level
                text1 = f"T-SPIN {NUMBER_TO_WORD[lines]}"
                text_alpha = 860
                self.game_state["b2b"] = True
        else:
            self.game_state["b2b"] = False
            score_increase += SCORING_BASE_VALUES[lines] * self.level
            text1 = f"{NUMBER_TO_WORD[lines]}"
            text_alpha = 800

        text2 += f"(+ {score_increase})"

        self.game_state["lines"] -= lines
        if self.game_state["lines"] <= 0:
            self.level += 1
            self.game_state["lines"] += self._lines_to_next()
            level_up = True
        self._increment_score(score_increase, level_up)
        self._surface_text.write(text1, text2, text_alpha)

    def render_hs(self):
        hs_surface = pg.Surface(HSCORE_SIZE)
        hs_surface.fill(GRID_COLOUR)
        text = FONT.render("HIGH SCORE:", True, TEXT_COLOUR)
        score_text = FONT.render(str(get_high_score()), True, TEXT_COLOUR)
        score_x_pos = SCORE_SIZE[0] - score_text.get_rect().width - MARGIN
        hs_surface.blit(text, (15, MARGIN))
        hs_surface.blit(score_text, (score_x_pos, FONT_SIZE + MARGIN))
        self.display.blit(hs_surface, HSCORE_COORDS)

    def pause(self, text="GAME PAUSED"):
        message = BIG_FONT.render(text, True, TEXT_COLOUR)
        sub_message = FONT.render("Press Escape to Continue", True, TEXT_COLOUR)
        message_pos = FIELD_SIZE[0] // 2 - message.get_rect().width // 2, FIELD_SIZE[1] // 2 - 50
        sub_message_pos = FIELD_SIZE[0] // 2 - sub_message.get_rect().width // 2, FIELD_SIZE[1] // 2 + 50
        self._surface_field.surface.blit(message, message_pos)
        self._surface_field.surface.blit(sub_message, sub_message_pos)
        self.display.blit(self._surface_field.surface, FIELD_COORDS)
        pg.display.flip()
        paused = True
        while paused and self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        paused = False
