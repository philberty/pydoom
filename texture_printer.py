from PyDoom.WadSprite import WadSprite
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

    for texture in wad.texture1.textures:
        for patch in texture.patches:
            path = "textures/{0}_{1}.jpeg".format(texture.name, patch.patch_name)
            picture = WadSprite.get_wad_picture_for_lump(patch.patch_lump)
            print("trying to save: {0}".format(path))
            picture.save_jpeg(path, wad.playpals[patch.colormap])


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()