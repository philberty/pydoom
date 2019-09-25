import logging
import optparse
import sys

from PyDoom.WadFile import WadFile


def main():
    parser = optparse.OptionParser()
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("No specified input wad-file provided")

    input_wad_file = args[0]
    wad = WadFile.load(input_wad_file)

    for key in wad.flats:
        picture = wad.flats[key]
        path = "flats/{0}.jpeg".format(picture.name)
        print("trying to save: {0}".format(path))
        picture.save_jpeg(path, wad.playpals[0])


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
