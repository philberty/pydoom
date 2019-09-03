from PyDoom.WadDirectory import WadDirectory
from PyDoom.WadElement import WadElement

import struct


class WadPnames(WadElement):

    """
    https://doom.fandom.com/wiki/PNAMES
    """

    def __init__(self, directory: WadDirectory):
        super(WadPnames, self).__init__()
        self._num_patches = struct.unpack("<L", directory.data[0:4])[0]
        self._patches = tuple(
            map(lambda i: directory.data[4 + ((i - 1) * 8):4 + (i * 8)].decode('utf-8').rstrip('\0'),
                range(1, self._num_patches + 1)))

    @property
    def num_patches(self):
        return self._num_patches

    @property
    def patches(self):
        return self._patches
