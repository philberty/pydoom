from PyDoom.WadElement import WadElement

import struct


class WadSector(WadElement):

    """
    http://doom.wikia.com/wiki/Sector
    """

    _floor_height = None
    _ceiling_height = None
    _floor_texture = None
    _ceiling_texture = None
    _light_level = None
    _sector_type = None
    _tag_number = None

    def __init__(self, chunk):
        super(WadSector, self).__init__()
        self._floor_height, self._ceiling_height = struct.unpack("<hh", chunk[0:4])
        self._floor_texture = chunk[4:12].decode('utf-8').rstrip('\0')
        self._ceiling_texture = chunk[12:20].decode('utf-8').rstrip('\0')
        self._light_level, self._sector_type, self._tag_number = struct.unpack("<hhh", chunk[20:26])

    @property
    def floor_height(self):
        return self._floor_height

    @property
    def ceiling_height(self):
        return self._ceiling_height

    @property
    def floor_texture(self):
        return self._floor_texture

    @property
    def ceiling_texture(self):
        return self._ceiling_texture

    @property
    def light_level(self):
        return self._light_level

    @property
    def sector_type(self):
        return self._sector_type

    @property
    def tag_number(self):
        return self._tag_number

    @staticmethod
    def element_size():
        return 26
