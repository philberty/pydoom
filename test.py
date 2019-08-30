from PyDoom.Definitions import Vertex

from typing import Tuple

import pygame
import time
import math


class Player:

    _position = Vertex(0, 0)
    _angle = 0.0  # 0 is north, clockwise, degrees

    @property
    def position(self):
        return self._position

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    def move_player_pos(self, mult, rotation_degrees):
        print("player was: {0}", self.position)
        self.position.x = self.position.x + math.sin(rad(self.angle + rotation_degrees)) * SPEED * mult
        self.position.y = self.position.y + math.cos(rad(self.angle + rotation_degrees)) * SPEED * mult
        print("player updated: {0}", self.position)


class Wall:

    def __init__(self, a, b, color):
        self._a = Vertex(a[0], a[1])
        self._b = Vertex(b[0], b[1])
        self._color = color

    @property
    def a(self) -> Vertex:
        return self._a

    @property
    def b(self) -> Vertex:
        return self._b

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._color


SPEED = 0.01
ROT_SPEED = 2
FRAME_MIN = 0.016
RAY_LENGTH = 0.1
WALL_COLOR = (150, 150, 150)
PLAYER_COLOR = (0, 255, 0)
PLAYER_RAY_COLOR = (255, 0, 0)


def rad(degrees):
    return degrees / 180 * math.pi


def screen_coords(x, y, screen_width=400, screen_height=400):
    coord = (x / 2 + 0.5) * screen_width, (-y / 2 + 0.5) * screen_height
    print("transforming {0}-{1} to {2}-{3}".format(x, y, coord[0], coord[1]))
    return coord


def main():
    pygame.init()
    width = 400
    height = 400
    screen_dimensions = width, height
    screen = pygame.display.set_mode(screen_dimensions)

    #     X  -1.5 | -1.0| -0.5|  0  | 0.5 | 1.0 | 1.5
    #     Y |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
    #   1.5 |  _  |  _  |  _  |  _  |  _  |  _  |  _  |
    #       |     |     |     |     |     |     |  _  |
    #    1  |  _  | AE  |  A  |  A  |  A  |  AB |  _  |
    #       |     |     |     |     |     |     |  _  |
    #  0.5  |  _  |  E  |  _  |  _  |  _  |  B  |  _  |
    #       |     |     |     |     |     |     |  _  |
    #    0  |  _  |  E  |  _  |  P  |  _  |  B  |  _  |
    #       |     |     |     |     |     |     |  _  |
    # -0.5  |  _  |  E  |  _  |  _  |  _  |  B  |  _  |
    #       |     |     |     |     |     |     |  _  |
    #   -1  |  _  | DE  |  _  |  _  |  _  |  BC |  _  |
    #       |     |     |     |     |     |     |  _  |
    # -1.5  |  _  |  _  |  D  |  _  |  C  |  _  |  _  |
    #       |  X  |  X  |  X  |  X  |  X  |  X  |  X  |

    walls = [
        Wall((-1.0, 1.0), (1.0, 1.0), (150, 150, 150)),     # A
        Wall((1.0, 1.0), (1.0, -1.0), (255, 150, 255)),     # B
        Wall((1.0, -1.0), (0.5, -1.5), (150, 255, 255)),    # C
        Wall((-0.5, -1.5), (-1.0, -1.0), (255, 255, 150)),  # D
        Wall((-1.0, -1.0), (-1.0, 1.0), (150, 255, 150)),   # E
    ]
    player = Player()

    prev_time = time.time()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.angle -= ROT_SPEED
        if keys[pygame.K_RIGHT]:
            player.angle += ROT_SPEED

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move_player_pos(1, 0)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move_player_pos(-1, 0)
        if keys[pygame.K_d]:
            player.move_player_pos(1, 90)
        if keys[pygame.K_a]:
            player.move_player_pos(-1, 90)

        # RENDER

        # video buffer
        surface = pygame.Surface((width, height))
        # clear
        surface.fill((0, 0, 0))

        for wall in walls:

            # Wall positions relative to player's position
            px1 = wall.a.x - player.position.x
            py1 = wall.a.y - player.position.y
            px2 = wall.b.x - player.position.x
            py2 = wall.b.y - player.position.y

            # player x=2 y=3
            # wall A begin x=0 y=1 end x=2 y=0
            # wall B begin x=0 y=2 end x=0 y=3

            # Y X 0  1  2  3  4
            #
            # 0   _  _  _  _  _
            #
            # 1   A  A  A  _  _
            #
            # 2   B  _  _  _  _
            #
            # 3   B  _  _  P  _
            #
            # 4   _  _  _  _  _

            # player x=2 y=3
            # wall A begin x=0 y=1 end x=2 y=0

            # B PX1 = 0 - 3 = -3
            #   PY1 = 1 - 3 = -2
            # E PX2 = 2 - 3 = -1
            #   PY2 = 3 - 3 = 0

            # rot = 0 rad
            # cos 0 = 1
            # sin 0 = 0

            # rx1 = math.cos(rad(-rot)) * px1 + math.sin(rad(-rot)) * py1
            #       (1 * -3) + (0 * -2) = -3
            # ry1 = math.cos(rad(-rot)) * py1 - math.sin(rad(-rot)) * px1
            #       (1 * -2) - (0 * -3) = -2
            # rx2 = math.cos(rad(-rot)) * px2 + math.sin(rad(-rot)) * py2
            #       (1 * -1) + (0 * 0) = -1
            # ry2 = math.cos(rad(-rot)) * py2 - math.sin(rad(-rot)) * px2
            #       (1 * 0) - (0 * -3) = 0

            # sin(angle) = opposite / hyp
            # cos(angle) = adjacent / hyp
            # tan(angle) = opposite / adjacent

            # Wall positions relative to player's position and rotation
            rx1 = math.cos(rad(-player.angle)) * px1 + math.sin(rad(-player.angle)) * py1
            ry1 = math.cos(rad(-player.angle)) * py1 - math.sin(rad(-player.angle)) * px1
            rx2 = math.cos(rad(-player.angle)) * px2 + math.sin(rad(-player.angle)) * py2
            ry2 = math.cos(rad(-player.angle)) * py2 - math.sin(rad(-player.angle)) * px2

            print("rx1 {0} ry1 {1} rx2 {2} ry2 {3}".format(rx1, ry1, rx2, ry2))

            pygame.draw.line(surface, wall.color,
                             screen_coords(rx1, ry1),
                             screen_coords(rx2, ry2), 1)

        # Draw player
        pygame.draw.line(surface, PLAYER_RAY_COLOR,
                         screen_coords(0, 0),
                         screen_coords(0, RAY_LENGTH), 1)
        pygame.draw.line(surface, PLAYER_COLOR,
                         screen_coords(0, 0),
                         screen_coords(0, 0), 1)

        # Render split screen
        screen.blit(surface, (0, 0))

        # Update screen
        pygame.display.update()

        # Sleep
        new_time = time.time()
        diff_time = new_time - prev_time
        prev_time = new_time
        if diff_time < FRAME_MIN:
            time.sleep(FRAME_MIN - diff_time)


if __name__ == "__main__":
    main()