Gfrom PyDoom.WadFile import WadFile
from PyDoom.PlayerState import Player
from PyDoom.WadLevel import WadLevel
from PyDoom.MathUtils import *
from PyDoom.Constants import *

import optparse
import logging
import pygame
import math
import time
import sys

from PyDoom.WadNode import WadNode

WIDTH = 640
HEIGHT = 480

WALL_HEIGHT = 50
CEILING_COLOR = (0, 0, 255)
FLOOR_COLOR = (255, 255, 0)


class Renderer:
    checkcoord = [
        [3, 0, 2, 1],
        [3, 0, 2, 0],
        [3, 1, 2, 0],
        [0],
        [2, 0, 2, 1],
        [0, 0, 0, 0],
        [3, 1, 3, 0],
        [0],
        [2, 0, 3, 1],
        [2, 1, 3, 1],
        [2, 1, 3, 0]
    ]

    def __init__(self, level: WadLevel, camera: Player, lines):
        self._level = level
        self._camera = camera
        self._bsp_node_index = len(self.level.nodes) - 1
        self._surface = None
        self._lines = lines
        self._lines_to_draw = None

    @property
    def level(self):
        return self._level

    @property
    def camera(self):
        return self._camera

    @property
    def surface(self):
        return self._surface

    @property
    def lines_to_draw(self):
        return self._lines_to_draw

    def point_on_side(self, node: WadNode):
        # node is vertical
        if node.delta_x > 0:
            print(1)
            if self.camera.position.x <= node.partiton_x:
                return 1 if node.delta_y > 0 else 0
            return 1 if node.delta_y < 0 else 0

        # node is horizontal
        if node.delta_y > 0:
            print(2)
            if self.camera.position.y <= node.partition_y:
                return 1 if node.delta_x < 0 else 0
            return 1 if node.delta_x > 0 else 0

        # calculate node to POV vector
        dx = self.camera.position.x - node.partiton_x
        dy = self.camera.position.y - node.partition_y

        # cross product here
        left = node.delta_y * dx
        right = dy * node.delta_x

        if right < left:
            return 0  # front side
        return 1  # back side

    def render_sub_sector(self, sub_sector_index):
        sub_sector = self.level.sub_sectors[sub_sector_index]

        first_seg_index = sub_sector.first_segment_index
        num_lines = sub_sector.segment_count

        for seg_index in range(first_seg_index, first_seg_index+num_lines):
            seg = self.level.segs[seg_index]
            self._lines_to_draw.append(self._lines[seg.linedef_index])

    def check_bounding_box(self, bspcoord):
        BOXTOP = 0
        BOXBOTTOM = 1
        BOXLEFT = 2
        BOXRIGHT = 3

        boxx = 0
        boxy = 0

        if self.camera.position.x <= bspcoord[BOXLEFT]:
            boxx = 0
        elif self.camera.position.x < bspcoord[BOXRIGHT]:
            boxx = 1
        else:
            boxx = 2

        if self.camera.position.y >= bspcoord[BOXTOP]:
            boxy = 0
        elif self.camera.position.y > bspcoord[BOXBOTTOM]:
            boxy = 1
        else:
            boxy = 2

        boxpos = (boxy << 2) + boxx
        if boxpos == 5:
            return 1

        x1 = bspcoord[self.checkcoord[boxpos][0]]
        y1 = bspcoord[self.checkcoord[boxpos][1]]
        x2 = bspcoord[self.checkcoord[boxpos][2]]
        y2 = bspcoord[self.checkcoord[boxpos][3]]

        # check clip list for an open space
        angle1 = math.atan(x1 / y1) - self.camera.angle
        angle2 = math.atan(x2 / y2) - self.camera.angle

        span = angle1 - angle2

        # Sitting on a line?
        if span >= 180:
            return 1

        return 0

    def render_bsp_node(self, bspnum):
        found_sub_sector = bspnum & 0x8000 == 0x8000

        if found_sub_sector:
            if bspnum == -1:
                self.render_sub_sector(0)
            else:
                maybe_node = bspnum + 0x8000
                self.render_sub_sector(maybe_node)
            return

        bsp = self._level.nodes[bspnum]
        side = self.point_on_side(bsp)

        self.render_bsp_node(bsp.children[side])

        # Possibly divide back space.
        if self.check_bounding_box(bsp.bounding_box_for_index(side ^ 1)):
            self.render_bsp_node(bsp.children[side ^ 1])

    def draw(self, surface):
        for line in self._lines_to_draw:
            # Wall absolute positions
            x1 = line.v1.x
            y1 = line.v1.y
            x2 = line.v2.x
            y2 = line.v2.y

            # Wall positions relative to player's position
            px1 = x1 - self.camera.position.x
            py1 = y1 - self.camera.position.y
            px2 = x2 - self.camera.position.x
            py2 = y2 - self.camera.position.y

            # Wall positions relative to player's position and rotation
            rx1 = math.cos(rad(-self.camera.angle)) * px1 + math.sin(rad(-self.camera.angle)) * py1
            ry1 = math.cos(rad(-self.camera.angle)) * py1 - math.sin(rad(-self.camera.angle)) * px1
            rx2 = math.cos(rad(-self.camera.angle)) * px2 + math.sin(rad(-self.camera.angle)) * py2
            ry2 = math.cos(rad(-self.camera.angle)) * py2 - math.sin(rad(-self.camera.angle)) * px2

            # Don't render walls behind us
            if ry1 <= 0 and ry2 <= 0:
                continue

            # Clip walls intersecting with user plane
            if ry1 <= 0 or ry2 <= 0:
                ix1 = intersect(rx1, ry1, rx2, ry2)
                if ry1 <= 0:
                    rx1 = ix1
                    ry1 = 0.01
                if ry2 <= 0:
                    rx2 = ix1
                    ry2 = 0.01

            # Wall positions relative to player's position, rotation and perspective
            zx1 = rx1 / ry1
            zu1 = WALL_HEIGHT / ry1  # Up   Z
            zd1 = -WALL_HEIGHT / ry1  # Down Z
            zx2 = rx2 / ry2
            zu2 = WALL_HEIGHT / ry2  # Up   Z
            zd2 = -WALL_HEIGHT / ry2  # Down Z

            poly = pygame.draw.polygon(surface, (100, 200, 150), [
                screen_coords_test(zx1, zd1),
                screen_coords_test(zx1, zu1),
                screen_coords_test(zx2, zu2),
                screen_coords_test(zx2, zd2)], 0)

    def render(self, surface):
        self._lines_to_draw = []
        self._surface = surface
        self.render_bsp_node(self._bsp_node_index)
        self.draw(surface)


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    level_to_render = "E1M1"

    level = wad.wad_levels[level_to_render]
    sectors, sides, lines, segs = level.compile_level()
    print("num sectors: {0}".format(len(sectors)))
    print("num sides: {0}".format(len(sides)))
    print("num lines: {0}".format(len(lines)))
    print("num segs: {0}".format(len(segs)))
    print("num nodes: {0}".format(len(level.nodes)))
    print("num vertexes: {0}".format(len(level.vertices)))
    print("num subsectors: {0}".format(len(level.sub_sectors)))

    for i in level.nodes:
        print(i)

    for i in level.things:
        print(i.definition)

    for i in level.sub_sectors:
        print(i)

    player_start = level.find_first_thing_by_name("PLAYER_1_START")
    print(player_start)

    root_node = level.root_node
    print(root_node)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH * 3, HEIGHT))
    pygame.display.set_caption("Render Player To Level {0} {1}".format(sys.argv[1], level_to_render))

    player = Player()
    player.position.x = player_start.x
    player.position.y = player_start.y
    player.angle = player_start.angle

    render = Renderer(level, player, lines)

    prev_time = time.time()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.angle = player.angle - ROT_SPEED
        if keys[pygame.K_RIGHT]:
            player.angle = player.angle + ROT_SPEED

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move_player_pos(3, 0)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move_player_pos(-3, 0)
        if keys[pygame.K_d]:
            player.move_player_pos(3, 180)
        if keys[pygame.K_a]:
            player.move_player_pos(-3, 180)

        # video buffer
        split_screen = pygame.Surface((WIDTH * 3, HEIGHT))
        # clear
        split_screen.fill((0, 0, 0))

        # Draw wall, floor and ceiling

        pygame.draw.rect(split_screen, CEILING_COLOR, pygame.Rect(0, 0, WIDTH, HEIGHT / 2))
        pygame.draw.rect(split_screen, FLOOR_COLOR, pygame.Rect(0, HEIGHT / 2, WIDTH, HEIGHT / 2))

        render.render(split_screen)

        # Render split screen
        screen.blit(split_screen, (0, 0))

        # render map BEGIN
        split_screen.fill((0, 0, 0))
        render_map(player, render.lines_to_draw, split_screen)
        screen.blit(split_screen, (WIDTH, 0))

        split_screen.fill((0, 0, 0))
        render_map(player, segs, split_screen)
        screen.blit(split_screen, (WIDTH * 2, 0))
        # render map DONE

        # Update screen
        pygame.display.update()

        # Sleep
        new_time = time.time()
        diff_time = new_time - prev_time
        prev_time = new_time
        if diff_time < FRAME_MIN:
            time.sleep(FRAME_MIN - diff_time)


def render_map(player, segs, split_screen):
    for line in segs:
        # Wall absolute positions
        x1 = line.v1.x
        y1 = line.v1.y
        x2 = line.v2.x
        y2 = line.v2.y

        # Wall positions relative to player's position
        px1 = x1 - player.position.x
        py1 = y1 - player.position.y
        px2 = x2 - player.position.x
        py2 = y2 - player.position.y

        # Wall positions relative to player's position and rotation
        rx1 = math.cos(rad(-player.angle)) * px1 + math.sin(rad(-player.angle)) * py1
        ry1 = math.cos(rad(-player.angle)) * py1 - math.sin(rad(-player.angle)) * px1
        rx2 = math.cos(rad(-player.angle)) * px2 + math.sin(rad(-player.angle)) * py2
        ry2 = math.cos(rad(-player.angle)) * py2 - math.sin(rad(-player.angle)) * px2

        begin = (rx1, ry1)
        end = (rx2, ry2)
        pygame.draw.line(split_screen, (150, 150, 150),
                         screen_coords(rx1, ry1),
                         screen_coords(rx2, ry2), 1)
    # Draw player
    pygame.draw.line(split_screen, PLAYER_RAY_COLOR,
                     screen_coords(0, 0),
                     screen_coords(0, RAY_LENGTH), 1)
    pygame.draw.line(split_screen, PLAYER_COLOR,
                     screen_coords(0, 0),
                     screen_coords(0, 0), 1)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
    
