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

    for thing in wad.wad_levels["E1M9"].things:
        if thing.has_sprite is False:
            continue

        print(thing.definition)
        for sprite in thing.sprite:
            path = "things/{0}.jpeg".format(sprite.name)
            print("trying to save:", path)
            sprite.save_jpeg(path, wad.playpals[0])


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()