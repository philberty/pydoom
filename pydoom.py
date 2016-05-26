from PyDoom.WadFile import WadFile
from PyDoom.MusDecoder import MusDecoder

import optparse
import sys


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    print("Loading: " + input_wad_file)
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
    level_music = wad['D_INTRO'][0]
    print("found music lump:", level_music)
    decoded = MusDecoder.decode_mus_to_midi(level_music)
    print("decoded music:", decoded)


if __name__ == "__main__":
    main()
