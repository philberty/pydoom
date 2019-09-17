#!/usr/bin/env python3

from PyDoom.WadFile import WadFile
from PyDoom.WadLevel import WadLevel

import optparse
import logging
import pygame
import sys

logger = logging.getLogger("pydoom")


class Renderer:

    def __init__(self, level: WadLevel, camera):
        self._level = level
        self._camera = camera

    @property
    def level(self):
        return self._level

    @property
    def camera(self):
        return self._camera


    def point_on_side(self, node):

        # node is vertical
        if ~node.delta_x:
            if x <= node.partiton_x:
                return node.delta_y > 0
            return node.delta_y < 0

        # node is horizontal
        if ~node.delta_y:
            if y <= node.partition_y:
                return node.delta_x < 0
            return node.delta_x > 0

        # calculate node to POV vector
        dx = x - node.parition_x
        dy = y - node.parition_y

        # Given a set of numbers where all elements occur even number of times except one number, find the odd occurring number
        # int arr[] = {12, 12, 14, 90, 14, 14, 14};
        # XOR sum will return 90
        if (node.delta_y ^ node.delta_x ^ dx ^ dy) < 0:
            if (node.delta_y ^ dx) < 0:
                # left is negative
                return 1
            return 0

        # cross product here
        left = node.delta_y * dx
        right = dy * node.delta_x

        if right < left:
            return 0  # front side
        return 1  # back side

    def render_bsp_node(self, bspnum):
        found_sub_sector = bspnum & 0x8000

        if found_sub_sector:
            if bspnum == -1:
                self.render_subsector(0)
            else:
                self.render_subsector(bspnum & (~0x8000000))
            return

        bsp = self._level.nodes[bspnum]
        side = self.point_on_side(self.view_x, self.view_y, bsp)

        self.render_bsp_node(bsp.children[side])



def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    level = wad.wad_levels["E1M1"]
    print(level)
    sectors, sides, lines, segs = level.compile_level()

    for i in level.things:
        print(i.definition.name)

    player_start = level.find_first_thing_by_name("PLAYER_1_START")
    print(player_start)



    pygame.init()
    width = 640
    height = 480
    screen_dimensions = width, height
    screen = pygame.display.set_mode(screen_dimensions)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False








        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
