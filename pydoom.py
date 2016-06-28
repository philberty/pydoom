#!/usr/bin/env python3

from PyDoom.WadFile import WadFile
from PyDoom.MusDecoder import MusDecoder

import logging
import optparse
import sys


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile(input_wad_file)

    #for level_key in wad.wad_levels:
    #    level = wad.wad_levels[level_key]
    #    level.save_svg()
    #    print("saved image of level [%s]" % level_key)

    #level = wad.wad_levels["E1M1"]
    #for i in level.things:
    #    print(i.thing_type)

    # to avoid conflict there can be multiple wad elements
    # of the same name so they are stored in a list
    level_music = wad['D_E1M1'][0]
    decoded = MusDecoder.decode_mus_to_midi(level_music)

    # test play midi file
    import pygame
    pygame.init()
    pygame.mixer.music.load(decoded)
    pygame.mixer.music.play(0)
    
    import time
    time.sleep(10)
    

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
