import pygame as pg
from bag import Bag
from playfield import Playfield
import tetrominoes as tet

WINDOW_SIZE = 720, 720
FPS = 60
SQUARE_SIZE = 35
FIELD_COORDS = 185, 10
FIELD_SIZE = 350, 700
GRID_DIMENSIONS = Playfield.get_dimensions()
GRID_WIDTH = 4
NEXT_SIZE = 150, 500
NEXT_COORDS = 555, 20
SCORE_SIZE = 150, 200
SCORE_COORDS = 15, 20
HOLD_SIZE = 150, 140
HOLD_COORDS = 15, 250
MARGIN = 10

pg.font.init()
FONT_SIZE = 45
FONT = pg.font.SysFont('Lucon.ttf', FONT_SIZE)
TEXT_COLOUR = (255, ) * 3

BG_COLOUR = (95,) * 3
GRID_COLOUR = (30,) * 3
EMPTY_COLOUR = (10,) * 3

MUSIC_FILE = "TetrisTheme.ogg"
VOLUME = 0.1
SCORING_BASE_VALUES = (40, 100, 300, 1200)


def draw_field(pf: Playfield):
    # field goes from top to bottom of window, and 175 pixels from each edge of window
    # each square is 35 x 35 pixels
    width, height = GRID_DIMENSIONS
    for i in range(height):
        for j in range(width):
            contents = pf.get_contents(j, height - i - 1)
            if contents is not None:
                draw_block(j, height - i - 1, contents)


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
    global cur_piece
    lines_cleared = cur_piece.place()
    if 0 < lines_cleared <= 4:
        global score, level, lines_to_next_level
        lines_to_next_level -= lines_cleared
        score += SCORING_BASE_VALUES[lines_cleared - 1] * level
        update_score()
        if lines_to_next_level <= 0:
            level += 1
            lines_to_next_level += 5 * level

    if field.garbage_out():
        return False
    cur_piece = tet.num_to_piece(selector.next())(field)
    update_next()
    cur_piece.drop()
    return True


def update_field():
    # clear field and redraw everything
    field_surface.fill(EMPTY_COLOUR)
    draw_field(field)
    draw_piece(cur_piece)
    draw_grid()
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
            offset = (HOLD_SIZE[0] // 8.5, HOLD_SIZE[1] // 8)
        else:
            offset = (HOLD_SIZE[0] // 4.5, HOLD_SIZE[1] // 8)
        draw_graphic_on(hold_surface, held.get_colour(), SQUARE_SIZE // 1.2, held.default_piece_positions(), offset, 2)
    hold_surface.blit(static_text, (25, MARGIN))
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
    score_surface.blit(static_text_2, (15, (FONT_SIZE + MARGIN) * 2))
    score_surface.blit(level_text, (level_x_pos, FONT_SIZE * 3 + MARGIN * 2))
    window.blit(score_surface, SCORE_COORDS)


def update_next():
    next_piece_surface.fill(GRID_COLOUR)
    static_text = FONT.render("NEXT:", True, TEXT_COLOUR)
    next_pieces = selector.show_next_n(6)
    for i, piece_num in enumerate(next_pieces):
        p_type = tet.num_to_piece(piece_num)
        if p_type == tet.IPiece:
            offset = (NEXT_SIZE[0] // 5, NEXT_SIZE[1] // 7 * i + 10)
        elif p_type == tet.OPiece:
            offset = (NEXT_SIZE[0] // 5, NEXT_SIZE[1] // 7 * i + 20)
        else:
            offset = (NEXT_SIZE[0] // 3.5, NEXT_SIZE[1] // 7 * i + 20)
        draw_graphic_on(next_piece_surface, p_type.get_colour(), SQUARE_SIZE // 1.5, p_type.default_piece_positions(),
                        offset, 1)
    next_piece_surface.blit(static_text, (30, MARGIN))
    window.blit(next_piece_surface, NEXT_COORDS)


def setup():
    pg.init()
    window.fill(BG_COLOUR)
    field_surface.fill(EMPTY_COLOUR)
    next_piece_surface.fill(GRID_COLOUR)
    score_surface.fill(GRID_COLOUR)
    hold_surface.fill(GRID_COLOUR)

    pg.mixer.music.load(MUSIC_FILE)
    pg.mixer.music.set_volume(VOLUME)
    pg.mixer.music.play(-1)

    update_score()
    update_hold_surface()
    update_next()
    pg.display.flip()


if __name__ == "__main__":
    # setup global variables
    window = pg.display.set_mode(WINDOW_SIZE)
    field_surface = pg.Surface(FIELD_SIZE)
    next_piece_surface = pg.Surface(NEXT_SIZE)
    score_surface = pg.Surface(SCORE_SIZE)
    hold_surface = pg.Surface(HOLD_SIZE)
    window_open = True
    selector = Bag()
    field = Playfield()
    cur_piece = tet.num_to_piece(selector.next())(field)
    level = 1
    next_move = FPS
    place_cd = 0
    score = 0
    held = None
    used_hold = 0
    lines_to_next_level = 5

    setup()

    while window_open:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                window_open = False
            elif event.type == pg.KEYDOWN:
                match event.key:
                    case pg.K_LEFT:
                        cur_piece.left()
                        place_cd = FPS // 2
                    case pg.K_RIGHT:
                        cur_piece.right()
                        place_cd = FPS // 2
                    case pg.K_DOWN:
                        cur_piece.drop()
                    case pg.K_SPACE:
                        cur_piece.hard_drop()
                        window_open = next_piece()
                        used_hold = False
                        next_move = FPS
                    case pg.K_x | pg.K_UP:
                        cur_piece.rotate_right()
                        place_cd = FPS // 2
                    case pg.K_z:
                        cur_piece.rotate_left()
                        place_cd = FPS // 2
                    case pg.K_c:
                        if not used_hold == 2:
                            used_hold += 1
                            if held is None:
                                held, cur_piece = cur_piece, tet.num_to_piece(selector.next())(field)
                                update_next()
                            else:
                                held, cur_piece = cur_piece, held
                                cur_piece.__init__(field)
                            update_hold_surface()
                            next_move = FPS

        next_move -= level
        if place_cd > 0:
            place_cd -= 1
        if next_move <= 0:
            next_move = FPS
            if not cur_piece.drop() and place_cd <= 0:
                window_open = next_piece()
                used_hold = 0

        update_field()

        pg.display.flip()
        pg.time.Clock().tick(FPS)
