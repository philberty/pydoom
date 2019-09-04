import math


def rad(degrees):
    return degrees / 180 * math.pi


def intersect(x1, y1, x2, y2):
    return (y1 * x2 - y2 * x1) / (y1 - y2)


#def screen_coords(x, y, screen_width=600, screen_height=600):
#    coord = (x / 2 + 0.5) * screen_width, (-y / 2 + 0.5) * screen_height
#    return coord

def screen_coords(x, y, screen_width=1280, screen_height=720):
    return (x + (screen_width / 2)), (-y + (screen_height / 2))


def screen_coords_test(x, y, screen_width=1280, screen_height=720):
    return (x / 2 + 0.5) * screen_width, (-y / 2 + 0.5) * screen_height