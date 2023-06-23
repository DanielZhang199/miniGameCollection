import pygame
import pygame as pg
from bag import Bag
from playfield import Playfield
import tetrominoes as tet

WINDOW_SIZE = 920, 840
FPS = 60  # should be multiple of 30 (but other speeds should work)
SQUARE_SIZE = 40
FIELD_COORDS = 240, 20
FIELD_SIZE = SQUARE_SIZE * 10, SQUARE_SIZE * 20  # currently 400 by 800
GRID_DIMENSIONS = Playfield.get_dimensions()
GRID_WIDTH = 4

NEXT_SIZE = 190, 480
NEXT_COORDS = 695, 20
HSCORE_SIZE = 230, 100
HSCORE_COORDS = 665, 520
SCORE_SIZE = 230, 180
SCORE_COORDS = 665, 640

HOLD_SIZE = 190, 140
HOLD_COORDS = 20, 20
TEXT_BOX_SIZE = 230, 200
TEXT_LOCATION = 15, 20

MARGIN = 15

pg.font.init()
FONT_SIZE = 45
FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE)
TEXT_COLOUR = (255,) * 3

BG_COLOUR = (95,) * 3
GRID_COLOUR = (30,) * 3
EMPTY_COLOUR = (10,) * 3

MUSIC_FILE = "TetrisTheme.ogg"
VOLUME = 0.1
SCORING_BASE_VALUES = {1: 100, 2: 300, 3: 500, 4: 800, "SoftDrop": 1, "HardDrop": 2, "Combo": 50,
                       "TSpin1": 800, "TSpin2": 1200, "TSpin3": 1600}  # zero line t-spin not implemented
BACK_TO_BACK_MULTIPLIER = 1.5   # for tetris and t spins
T_SPIN_KICK_PENALTY = 0.5  # not yet implemented
GHOST = True  # displays ghost of where piece will land
GHOST_ALPHA = 50

# Define movement constants
MOVE_DELAY = 10  # Frames between continuous movements
MOVE_REPEAT = 3  # Frames between subsequent continuous movements
SOFT_DROP_SPEED = 2  # Frames between subsequent drops in a soft drop
MIN_PLACE_DELAY = 45

INFINITY = False
MAX_ROTATES = 15


def draw_field(pf: Playfield):
    # field goes from top to bottom of window, and 175 pixels from each edge of window
    # each square is 35 x 35 pixels
    width, height = GRID_DIMENSIONS
    for i in range(height):
        for j in range(width):
            contents = pf.get_contents(j, height - i - 1)
            if contents is not None:
                draw_block(j, height - i - 1, contents)


def draw_ghost(coords, colour):
    for x, y in coords:
        draw_block_transparent(x, y, colour)


def draw_grid():
    for x in range(GRID_DIMENSIONS[0]):
        x *= SQUARE_SIZE
        pg.draw.line(field_surface, GRID_COLOUR, (x, 0), (x, FIELD_SIZE[1]), GRID_WIDTH)

    for y in range(GRID_DIMENSIONS[1]):
        y *= SQUARE_SIZE
        pg.draw.line(field_surface, GRID_COLOUR, (0, y), (FIELD_SIZE[0], y), GRID_WIDTH)

    # draw missing outline directly on game surface
    pg.draw.line(window, GRID_COLOUR, (FIELD_COORDS[0], FIELD_COORDS[1] + FIELD_SIZE[1]),
                 (FIELD_COORDS[0] + FIELD_SIZE[0], FIELD_COORDS[1] + FIELD_SIZE[1]), GRID_WIDTH)
    pg.draw.line(window, GRID_COLOUR, (FIELD_COORDS[0] + FIELD_SIZE[0], FIELD_COORDS[1]),
                 (FIELD_COORDS[0] + FIELD_SIZE[0], FIELD_COORDS[1] + FIELD_SIZE[1] + GRID_WIDTH // 2), GRID_WIDTH)


def draw_block(x, y, colour):
    x = x * SQUARE_SIZE
    y = FIELD_SIZE[1] - (y + 1) * SQUARE_SIZE
    pg.draw.rect(field_surface, colour, pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))


def draw_block_transparent(x, y, colour):
    x = x * SQUARE_SIZE
    y = FIELD_SIZE[1] - (y + 1) * SQUARE_SIZE
    draw_rect_alpha(field_surface, colour, pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))


def draw_rect_alpha(surface, color, rect):
    shape_surf = pg.Surface(pg.Rect(rect).size, pg.SRCALPHA)
    pg.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def draw_piece(piece: tet.Piece):
    coords = piece.get_coordinates()
    colour = piece.get_colour()
    for x, y in coords:
        draw_block(x, y, colour)


def next_piece():
    """
    this subroutine is probably not best code design, but I don't really care at this point.
    :return: (whether the game is over or not)
    """
    global cur_piece, ghost_coords, countdown_activated, place_countdown, rotates_remaining, last_movement, combo_count
    is_t_spin = type(cur_piece) == tet.TPiece and last_movement == "ROTATE" and cur_piece.t_spin_corners_satisfied()
    lines_cleared = cur_piece.place()
    if lines_cleared > 0:
        global score, level, lines_to_next_level, can_b2b
        combo_count += 1
        if combo_count > 0:
            score += SCORING_BASE_VALUES["Combo"] * level * combo_count
            print("COMBO: " + str(combo_count))

        if lines_cleared == 4:
            if can_b2b:
                score += int(SCORING_BASE_VALUES[4] * level * BACK_TO_BACK_MULTIPLIER)  # the multiplier is a float
                print("B2B TETRIS")
            else:
                score += SCORING_BASE_VALUES[4] * level
                print("TETRIS")
                can_b2b = True
        elif is_t_spin:
            if can_b2b:
                score += int(SCORING_BASE_VALUES["TSpin" + str(lines_cleared)] * level * BACK_TO_BACK_MULTIPLIER)
                print("B2B T-SPIN (" + str(lines_cleared) + " lines)")
            else:
                score += SCORING_BASE_VALUES["TSpin" + str(lines_cleared)] * level
                print("T-SPIN (" + str(lines_cleared) + " lines)")
                can_b2b = True
        elif 0 < lines_cleared <= 3:
            can_b2b = False
            score += SCORING_BASE_VALUES[lines_cleared] * level

        lines_to_next_level -= lines_cleared
        if lines_to_next_level <= 0:
            level += 1
            lines_to_next_level += get_lines_to_next_level()
    else:
        if combo_count > 0:
            print("COMBO BREAK")
        combo_count = -1

    if field.garbage_out():
        return False
    cur_piece = tet.num_to_piece(selector.next())(field)
    update_next()
    cur_piece.drop()
    ghost_coords = cur_piece.get_ghost_coords()
    place_countdown = MIN_PLACE_DELAY
    countdown_activated = False
    rotates_remaining = MAX_ROTATES
    last_movement = None
    return True


def update_field():
    # clear field and redraw everything
    field_surface.fill(EMPTY_COLOUR)
    draw_field(field)
    draw_piece(cur_piece)
    draw_grid()
    if GHOST:
        draw_ghost(ghost_coords, cur_piece.get_colour() + (GHOST_ALPHA, ))
    window.blit(field_surface, FIELD_COORDS)


def draw_graphic_on(surface, colour, size, coords, offset, border):
    for x, y in coords:
        x = x * size + offset[0]
        y = y * size + FONT_SIZE + offset[1]
        if border > 0:
            pg.draw.rect(surface, (0, 0, 0), pg.Rect(x, y, size, size))
        pg.draw.rect(surface, colour, pg.Rect(x + border, y + border, size - border * 2, size - border * 2))


def update_hold_surface():
    hold_surface.fill(GRID_COLOUR)
    static_text = FONT.render("HOLD:", True, TEXT_COLOUR)
    if held is not None:  # so it doesn't crash randomly
        if type(held) == tet.IPiece or type(held) == tet.OPiece:
            offset = (HOLD_SIZE[0] // 7, HOLD_SIZE[1] // 9)
        else:
            offset = (HOLD_SIZE[0] // 4, HOLD_SIZE[1] // 9)
        draw_graphic_on(hold_surface, held.get_colour(), SQUARE_SIZE // 1.2, held.default_piece_positions(), offset, 2)
    hold_surface.blit(static_text, (45, MARGIN))
    window.blit(hold_surface, HOLD_COORDS)


def update_score():
    # updates score and level counter surface using the globally defined values
    score_surface.fill(GRID_COLOUR)
    static_text_1 = FONT.render("SCORE:", True, TEXT_COLOUR)
    static_text_2 = FONT.render("LEVEL:", True, TEXT_COLOUR)
    score_text = FONT.render(str(score), True, TEXT_COLOUR)
    level_text = FONT.render(str(level), True, TEXT_COLOUR)
    score_x_pos = SCORE_SIZE[0] - score_text.get_rect().width - MARGIN
    level_x_pos = SCORE_SIZE[0] - level_text.get_rect().width - MARGIN
    score_surface.blit(static_text_1, (15, MARGIN))
    score_surface.blit(score_text, (score_x_pos, FONT_SIZE + MARGIN))
    score_surface.blit(level_text, (level_x_pos, FONT_SIZE * 2 + MARGIN * 3))
    score_surface.blit(static_text_2, (15, FONT_SIZE * 2 + MARGIN * 3))
    window.blit(score_surface, SCORE_COORDS)


def update_next():
    next_piece_surface.fill(GRID_COLOUR)
    static_text = FONT.render("NEXT:", True, TEXT_COLOUR)
    next_pieces = selector.show_next_n(5)
    for i, piece_num in enumerate(next_pieces):
        p_type = tet.num_to_piece(piece_num)
        if p_type == tet.IPiece:
            offset = (NEXT_SIZE[0] // 5, NEXT_SIZE[1] // 5.7 * i + 5)
        elif p_type == tet.OPiece:
            offset = (NEXT_SIZE[0] // 5, NEXT_SIZE[1] // 5.7 * i + 15)
        else:
            offset = (NEXT_SIZE[0] // 3.5, NEXT_SIZE[1] // 5.7 * i + 15)
        draw_graphic_on(next_piece_surface, p_type.get_colour(), SQUARE_SIZE // 1.2, p_type.default_piece_positions(),
                        offset, 2)
    next_piece_surface.blit(static_text, (50, MARGIN))
    window.blit(next_piece_surface, NEXT_COORDS)


def setup():
    pg.init()
    pg.display.set_caption('Almost Tetris')

    window.fill(BG_COLOUR)
    field_surface.fill(EMPTY_COLOUR)
    next_piece_surface.fill(GRID_COLOUR)
    score_surface.fill(GRID_COLOUR)
    hold_surface.fill(GRID_COLOUR)

    pg.mixer.music.load(MUSIC_FILE)
    pg.mixer.music.set_volume(VOLUME)
    pg.mixer.music.play(-1)

    update_hold_surface()
    update_next()

    hs_surface = pygame.Surface(HSCORE_SIZE)
    hs_surface.fill(GRID_COLOUR)
    text = FONT.render("HIGH SCORE:", True, TEXT_COLOUR)
    score_text = FONT.render(str(HIGH_SCORE), True, TEXT_COLOUR)
    score_x_pos = SCORE_SIZE[0] - score_text.get_rect().width - MARGIN
    hs_surface.blit(text, (15, MARGIN))
    hs_surface.blit(score_text, (score_x_pos, FONT_SIZE + MARGIN))
    window.blit(hs_surface, HSCORE_COORDS)

    pg.display.flip()


def get_new_next_move_val():
    # return either FPS - level * FPS // 10 (linear decrease from 1 second to 0 seconds over 15 levels)
    # or minimum of 2 frames
    # while levels can exceed 15, the actual speed will never exceed that of level 15 (levels start at 1)
    return max(FPS - (level - 1) * FPS // 20, 2)


def get_lines_to_next_level():
    return 4 + level


def get_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        with open("high_score.txt", "w") as f:
            f.write("0")
            return 0


def write_high_score(num):
    with open("high_score.txt", "w") as f:
        f.write(str(num))


def write_impact_text(text):
    pass


if __name__ == "__main__":
    # setup global variables
    clock = pygame.time.Clock()
    window = pg.display.set_mode(WINDOW_SIZE)
    field_surface = pg.Surface(FIELD_SIZE)
    next_piece_surface = pg.Surface(NEXT_SIZE)
    score_surface = pg.Surface(SCORE_SIZE)
    hold_surface = pg.Surface(HOLD_SIZE)
    text_surface = pg.Surface(TEXT_BOX_SIZE, pg.SRCALPHA)
    window_open = True
    selector = Bag()
    field = Playfield()
    level = 1
    score = 0

    cur_piece = tet.num_to_piece(selector.next())(field)
    next_move = get_new_next_move_val()
    place_countdown = MIN_PLACE_DELAY
    countdown_activated = False
    rotates_remaining = MAX_ROTATES
    combo_count = -1
    can_b2b = False
    held = None
    used_hold = 0
    move_timer = 0
    drop_timer = 0
    last_movement = None
    lines_to_next_level = get_lines_to_next_level()
    ghost_coords = cur_piece.get_ghost_coords()
    HIGH_SCORE = get_high_score()

    setup()

    while window_open:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                window_open = False
            elif event.type == pg.KEYDOWN:
                match event.key:
                    case pg.K_LEFT:
                        move_timer = 0
                        if cur_piece.left():
                            ghost_coords = cur_piece.get_ghost_coords()
                            last_movement = "LEFT"
                    case pg.K_RIGHT:
                        move_timer = 0
                        if cur_piece.right():
                            ghost_coords = cur_piece.get_ghost_coords()
                            last_movement = "RIGHT"
                    case pg.K_DOWN:
                        drop_timer = 0
                        if cur_piece.drop():
                            last_movement = "DOWN"
                            score += SCORING_BASE_VALUES["SoftDrop"]
                    case pg.K_SPACE:
                        score += SCORING_BASE_VALUES["HardDrop"] * cur_piece.hard_drop()
                        last_movement = "DOWN"
                        window_open = next_piece()
                        used_hold = False
                        next_move = get_new_next_move_val()
                    case pg.K_x | pg.K_UP:
                        cur_piece.rotate_right()
                        last_movement = "ROTATE"
                        ghost_coords = cur_piece.get_ghost_coords()
                        if rotates_remaining >= 0:
                            place_countdown = MIN_PLACE_DELAY
                            if not INFINITY and countdown_activated:
                                rotates_remaining -= 1
                    case pg.K_z:
                        cur_piece.rotate_left()
                        last_movement = "ROTATE"
                        ghost_coords = cur_piece.get_ghost_coords()
                        if rotates_remaining >= 0:
                            place_countdown = MIN_PLACE_DELAY
                            if not INFINITY and countdown_activated:
                                rotates_remaining -= 1
                    case pg.K_c:
                        if not used_hold == 2:
                            used_hold += 1
                            place_countdown = MIN_PLACE_DELAY
                            countdown_activated = False
                            rotates_remaining = MAX_ROTATES
                            last_movement = None
                            if held is None:
                                held, cur_piece = cur_piece, tet.num_to_piece(selector.next())(field)
                                update_next()
                            else:
                                held, cur_piece = cur_piece, held
                                cur_piece.__init__(field)
                            update_hold_surface()
                            next_move = get_new_next_move_val()
                            ghost_coords = cur_piece.get_ghost_coords()

        keys = pygame.key.get_pressed()
        if keys[pg.K_LEFT]:
            move_timer += 1  # keep track of how long key has been held
            if move_timer >= MOVE_DELAY:
                if cur_piece.left():
                    move_timer -= MOVE_REPEAT
                    ghost_coords = cur_piece.get_ghost_coords()
                    last_movement = "LEFT"
        elif keys[pg.K_RIGHT]:
            move_timer += 1
            if move_timer >= MOVE_DELAY:
                if cur_piece.right():
                    move_timer -= MOVE_REPEAT
                    ghost_coords = cur_piece.get_ghost_coords()
                    last_movement = "RIGHT"
        if keys[pg.K_DOWN]:
            drop_timer += 1
            if drop_timer >= MOVE_DELAY:
                drop_timer -= SOFT_DROP_SPEED
                if cur_piece.drop():
                    score += SCORING_BASE_VALUES["SoftDrop"]
                    last_movement = "DOWN"

        next_move -= 1
        if next_move <= 0:
            next_move = get_new_next_move_val()
            if not cur_piece.drop():
                if place_countdown <= 0:
                    window_open = next_piece()
                    used_hold = 0
                countdown_activated = True

        if countdown_activated:
            place_countdown -= 1

        update_field()
        update_score()

        pg.display.flip()
        pg.time.Clock().tick(FPS)

    if score > HIGH_SCORE:
        write_high_score(score)
