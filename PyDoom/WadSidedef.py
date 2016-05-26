from PyDoom.WadElement import WadElement

import struct


class WadSidedef(WadElement):

    """
    http://doom.wikia.com/wiki/Sidedef
    """

    _x_offset = None
    _y_offset = None
    _name_of_upper_texture = None
    _name_of_lower_texture = None
    _name_of_middle_texture = None
    _sector_number = None

    def __init__(self, chunk):
        super(WadSidedef, self).__init__()
        self._x_offset, self._y_offset = struct.unpack('<hh', chunk[0:4])
        self._name_of_upper_texture = chunk[4:12].decode('utf-8').rstrip('\0')
        self._name_of_lower_texture = chunk[12:20].decode('utf-8').rstrip('\0')
        self._name_of_middle_texture = chunk[20:28].decode('utf-8').rstrip('\0')
        self._sector_number = struct.unpack('<h', chunk[28:30])

    @property
    def x_offset(self):
        return self._x_offset

    @property
    def y_offset(self):
        return self._y_offset

    @property
    def name_of_upper_texture(self):
        return self._name_of_upper_texture

    @property
    def name_of_lower_texture(self):
        return self._name_of_lower_texture

    @property
    def name_of_middle_texture(self):
        return self._name_of_middle_texture

    @staticmethod
    def element_size():
        return 30