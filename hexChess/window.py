import tkinter as tk

colours = {0: "#fff", 1: "#aaa", 2: "#888"}


def draw_hexagon(canvas, x, y, size, colour):
    hex_coords = [
        x - size, y,
        x - size/2, y - size * 0.866,
        x + size/2, y - size * 0.866,
        x + size, y,
        x + size/2, y + size * 0.866,
        x - size/2, y + size * 0.866
    ]
    canvas.create_polygon(hex_coords, outline='black', fill=colour)


def create_hexagon_window():
    window = tk.Tk()
    window.title('Hexagon Window')

    canvas = tk.Canvas(window, width=1000, height=1000)
    canvas.pack()

    hex_radius = 50  # radius of 50 (long diagonal of 100)

    columns = "abcdefghijk"
    center = len(columns) // 2 + 1  # =6

    start_x = 130
    start_y = 75
    x = start_x
    squares_coord_map = {}

    last_row_colour = -1
    for i, col in enumerate(columns):
        if i < center:
            num_rows = i + center
            last_row_colour += 1
            if last_row_colour > 2:
                last_row_colour = 0
        else:
            num_rows = 2 * center - i + 4
            last_row_colour -= 1
            if last_row_colour < 0:
                last_row_colour = 2
        y = start_y + (len(columns) - num_rows) * hex_radius * (13 / 15)  # apothem is 13/15 of the radius
        next_colour = last_row_colour
        for row in range(num_rows, 0, -1):
            draw_hexagon(canvas, x, y, hex_radius, colours[next_colour])
            canvas.create_text(x, y, text=f"{i + 1}, {row}\n({col}{row})", fill="black", font='Helvetica 15 bold')
            next_colour += 1
            if next_colour > 2:
                next_colour = 0
            y += hex_radius * (26 / 15)   # height of each hex is two times apothem
            squares_coord_map[f"{col}{row}"] = x, y

        x += hex_radius * 1.5
        # width of hexagon is 2 times radius, but we inset each new column halfway into second radius to form grid

    # print(squares_coord_map)
    window.mainloop()


if __name__ == "__main__":
    create_hexagon_window()
