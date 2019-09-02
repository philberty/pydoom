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


WIDTH = 1024
HEIGHT = 768

WALL_HEIGHT = 0.25
CEILING_COLOR = (0, 0, 255)
FLOOR_COLOR = (255, 255, 0)


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    level = wad.wad_levels["E1M1"]
    sectors, sides, lines, segs = level.compile_level()
    print("num sectors: {0}".format(len(sectors)))
    print("num sides: {0}".format(len(sides)))
    print("num lines: {0}".format(len(lines)))
    print("num segs: {0}".format(len(segs)))
    print("num nodes: {0}".format(len(level.nodes)))
    print("num vertexes: {0}".format(len(level.vertices)))
    print("num subsectors: {0}".format(len(level.sub_sectors)))

    level.save_svg('./test.svg')

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
            player.move_player_pos(1, 0)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move_player_pos(-1, 0)
        if keys[pygame.K_d]:
            player.move_player_pos(1, 90)
        if keys[pygame.K_a]:
            player.move_player_pos(-1, 90)

        # video buffer
        split_screen = pygame.Surface((WIDTH, HEIGHT))
        # clear
        split_screen.fill((0, 0, 0))

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
