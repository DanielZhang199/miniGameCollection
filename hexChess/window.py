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

    hex_size = 50

    num_columns = 11
    center = num_columns // 2 + 1  # =6

    start_x = 130
    start_y = 75
    x = start_x

    last_row_colour = -1
    for col in range(num_columns):
        if col < center:
            num_rows = col + center
            last_row_colour += 1
            if last_row_colour > 2:
                last_row_colour = 0
        else:
            num_rows = num_columns - col + center - 1
            last_row_colour -= 1
            if last_row_colour < 0:
                last_row_colour = 2
        y = start_y + (num_columns - num_rows) * hex_size * 0.866
        next_colour = last_row_colour
        for row in range(num_rows):
            draw_hexagon(canvas, x, y, hex_size, colours[next_colour])
            next_colour += 1
            if next_colour > 2:
                next_colour = 0
            y += hex_size * 1.67

        x += hex_size * 1.5


    window.mainloop()


if __name__ == "__main__":
    create_hexagon_window()
