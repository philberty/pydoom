#!/usr/bin/env python3

from PyDoom.MusDecoder import MusDecoder
from PyDoom.WadFile import WadFile

import optparse
import logging
import sys


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    # for level_key in wad.wad_levels:
    #     level = wad.wad_levels[level_key]
    #     print (level_key, level)
    #     level.save_svg()
    #     print("saved image of level [%s]" % level_key)

    level2_zombies = tuple(filter(lambda t: t.definition.name == \
                                  "FORMER_HUMAN",
                                  wad.wad_levels["E1M2"].things))

    zombie = level2_zombies[0]
    zombieSprite = zombie.sprite
    
    for zombieLumpIndex in range(len(zombieSprite)):
        zombiePicture = zombieSprite.getDoomPicture(zombieLumpIndex)
        zombiePrefix = zombie.definition.name + "_" + zombiePicture.name
        zPath = zombiePrefix + '.png'
        print("saving:", zPath)
        zombiePicture.savePng(zPath, wad.playpals[0])
    

    # to avoid conflict there can be multiple wad elements
    # of the same name so they are stored in a list
    # level_music = wad['D_E1M1'][0]
    # decoded = MusDecoder.decode_mus_to_midi(level_music)
    
    # with open('encoded_e1m1.mid', 'wb') as fd:
    #     fd.write(decoded)
    

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
