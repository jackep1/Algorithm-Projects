import copy
from tkinter import Button
from tkinter import Canvas
from tkinter import NORMAL
from tkinter import PhotoImage
from tkinter import Tk

from convex_hull import compute_hull, base_case_hull


def draw_point(canvas, x, y):
    point_radius = 3  # Radius of the point for visualization

    # Create an oval shape centered on (x, y) with the specified radius
    # The oval represents the point
    return canvas.create_oval(
        x - point_radius, y - point_radius, 
        x + point_radius, y + point_radius, 
        fill="black", outline="red"
    )



def add_point(event):
    draw_point(w, event.x, event.y)
    points.append((event.x, event.y))
    return


def draw_hull():
    hull = copy.copy(compute_hull(points))
    hull.append(hull[0])
    for i in range(0, len(hull) - 1):
        x1 = hull[i][0]
        y1 = hull[i][1]
        x2 = hull[i + 1][0]
        y2 = hull[i + 1][1]
        w.create_line(x1, y1, x2, y2, width=3)
    return

def clear_canvas(canvas, pts):
    canvas.delete("all")
    pts.clear()
    return


if __name__ == '__main__':
    master, points = Tk(), list()

    submit_button = Button(master, text="Draw Hull", command=draw_hull)
    submit_button.pack()
    quit_button = Button(master, text="Quit", command=master.quit)
    quit_button.pack()
    erase_button = Button(master, text="Erase", command=lambda: clear_canvas(w, points))
    erase_button.pack()

    canvas_width = 1000
    canvas_height = 800
    w = Canvas(master,
            width=canvas_width,
            height=canvas_height)

    w.pack()
    w.bind('<Button-1>', add_point)

    w.mainloop()
