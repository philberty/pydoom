from PyDoom.WadElement import WadElement

import struct


class WadBlockmap(WadElement):

    """
    http://doom.wikia.com/wiki/Blockmap
    """

    def __init__(self, chunk):
        super(WadBlockmap, self).__init__()
