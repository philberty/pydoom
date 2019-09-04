from PyDoom.WadFile import WadFile
from PyDoom.PlayerState import Player
from PyDoom.MathUtils import *
from PyDoom.Constants import *

import optparse
import logging
import pygame
import math
import time
import sys


WIDTH = 1280
HEIGHT = 720

WALL_HEIGHT = 50
CEILING_COLOR = (0, 0, 255)
FLOOR_COLOR = (255, 255, 0)


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
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Render Player To Level {0} {1}".format(sys.argv[1], level_to_render))

    player = Player()
    player.position.x = player_start.x
    player.position.y = player_start.y
    player.angle = player_start.angle

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
        split_screen = pygame.Surface((WIDTH, HEIGHT))
        # clear
        split_screen.fill((0, 0, 0))

        # Draw wall, floor and ceiling

        pygame.draw.rect(split_screen, CEILING_COLOR, pygame.Rect(0, 0, WIDTH, HEIGHT / 2))
        pygame.draw.rect(split_screen, FLOOR_COLOR, pygame.Rect(0, HEIGHT / 2, WIDTH, HEIGHT / 2))

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

            # zx1 = rx1 / ry1
            # zu1 = WALL_HEIGHT / ry1  # Up   Z
            # zd1 = -WALL_HEIGHT / ry1  # Down Z
            # zx2 = rx2 / ry2
            # zu2 = WALL_HEIGHT / ry2  # Up   Z
            # zd2 = -WALL_HEIGHT / ry2  # Down Z

            poly = pygame.draw.polygon(split_screen, (100, 200, 150), [
                screen_coords_test(zx1, zd1),
                screen_coords_test(zx1, zu1),
                screen_coords_test(zx2, zu2),
                screen_coords_test(zx2, zd2)], 0)

            #if line.side.top_texture:
            #    for t in line.side.top_texture.textures:
            #        for patch in t.patches:


        # Render split screen
        screen.blit(split_screen, (0, 0))

        # Update screen
        pygame.display.update()

        # Sleep
        new_time = time.time()
        diff_time = new_time - prev_time
        prev_time = new_time
        if diff_time < FRAME_MIN:
            time.sleep(FRAME_MIN - diff_time)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
