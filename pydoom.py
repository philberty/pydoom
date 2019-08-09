#!/usr/bin/env python3

from PyDoom.MusDecoder import MusDecoder
from PyDoom.WadSprite import WadPicture
from PyDoom.WadFile import WadFile

import optparse
import logging
import pygame
import time
import sys
import os
import io


logger = logging.getLogger ("pydoom")



def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    # to avoid conflict there can be multiple wad elements
    # of the same name so they are stored in a list
    level_music = wad['D_E1M1'][0]
    decoded_music = MusDecoder.decode_mus_to_midi(level_music)

    with open('music.mid', 'wb') as fd:
        fd.write(decoded_music)

    # test play midi file
    import pygame
    pygame.init()
    pygame.mixer.music.load(decoded_music)
    pygame.mixer.music.play()

    import time
    time.sleep(10)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
