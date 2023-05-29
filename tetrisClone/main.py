import pygame as pg
from bag import Bag
from playfield import Playfield
import tetrominoes as tet

WINDOW_SIZE = 1280, 1280
SURFACE_SIZE = 720, 720
FPS = 10
SQUARE_SIZE = 35
FIELD_OFFSET = 185, 10
FIELD_SIZE = 350, 700
GRID_DIMENSIONS = Playfield.get_dimensions()
GRID_WIDTH = 4

BG_COLOUR = (95,) * 3
GRID_COLOUR = (30,) * 3
EMPTY_COLOUR = (10,) * 3


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
        pg.draw.line(display_field, GRID_COLOUR, (x, 0), (x, FIELD_SIZE[1]), GRID_WIDTH)

    for y in range(GRID_DIMENSIONS[1]):
        y *= SQUARE_SIZE
        pg.draw.line(display_field, GRID_COLOUR, (0, y), (FIELD_SIZE[0], y), GRID_WIDTH)

    # draw missing outline directly on game surface
    pg.draw.line(surface, GRID_COLOUR, (FIELD_OFFSET[0], FIELD_OFFSET[1] + FIELD_SIZE[1]),
                 (FIELD_OFFSET[0] + FIELD_SIZE[0], FIELD_OFFSET[1] + FIELD_SIZE[1]), GRID_WIDTH)
    pg.draw.line(surface, GRID_COLOUR, (FIELD_OFFSET[0] + FIELD_SIZE[0], FIELD_OFFSET[1]),
                 (FIELD_OFFSET[0] + FIELD_SIZE[0], FIELD_OFFSET[1] + FIELD_SIZE[1] + GRID_WIDTH // 2), GRID_WIDTH)


def draw_block(x, y, colour):
    x = x * SQUARE_SIZE
    y = FIELD_SIZE[1] - (y + 1) * SQUARE_SIZE
    pg.draw.rect(display_field, colour, pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))


def draw_piece(piece: tet.Piece):
    coords = piece.get_coordinates()
    colour = piece.get_colour()
    for x, y in coords:
        draw_block(x, y, colour)


def display_next(pieces):
    pass


if __name__ == "__main__":
    pg.init()
    window = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE)
    surface = pg.Surface(SURFACE_SIZE)
    surface.fill(BG_COLOUR)
    display_field = pg.Surface(FIELD_SIZE)
    display_field.fill(EMPTY_COLOUR)
    window_open = True

    selector = Bag()
    field = Playfield()
    for i in range(7):
        cur_piece = tet.num_to_piece(field, selector.next())
        cur_piece.hard_drop()
    cur_piece = tet.num_to_piece(field, selector.next())
    cur_piece.drop()
    cur_piece.drop()

    while window_open:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                window_open = False

        draw_field(field)
        draw_piece(cur_piece)
        draw_grid()

        surface.blit(display_field, FIELD_OFFSET)
        window.blit(pg.transform.scale(surface, window.get_rect().size), (0, 0))
        pg.display.flip()
        pg.time.Clock().tick(FPS)
