from PyDoom.WadFile import WadFile

import optparse
import logging
import pygame
import sys


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

    root_node = level.root_node
    # print(root_node)

    for i in level.nodes:
        print(i)

    for i in level.things:
        print(i.definition.name)

    player_start = level.find_first_thing_by_name("PLAYER_1_START")
    print(player_start)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
