from PyDoom.WadElement import WadElement

import struct

# Linedefs contain a two-byte (16 bit) field reserved for various flags. Flags are as follows:
# 0 0x0001	blocks players and monsters
# 1 0x0002	blocks monsters
# 2 0x0004	two sided
# 3 0x0008	upper texture is unpegged
# 4 0x0010	lower texture is unpegged
# 5 0x0020	secret (shows as one-sided on automap), and monsters cannot open if it is a door (type 1)
# 6 0x0040	blocks sound
# 7 0x0080	never shows on automap
# 8 0x0100	always shows on automap

class WadLinedef(WadElement):

    """
    http://doom.wikia.com/wiki/Linedef - specification
    """

## Fields

    _start_vertex = 0
    _end_vertex = 0
    _flags = 0
    _special_type = 0
    _sector_tag = 0
    _right_sidedef = 0
    _left_sidedef = 0

## Constructor

    def __init__(self, chunk):
        """
        Parses the linedef chunk into its elements

        :param chunk: the linedef byte-buffer
        :return: new linedef
        """
        super(WadLinedef, self).__init__()
        self._start_vertex, \
            self._end_vertex, \
            self._flags, \
            self._special_type, \
            self._sector_tag, \
            self._right_sidedef, \
            self._left_sidedef = struct.unpack('<hhhhhhh', chunk)

## Properties

    @property
    def start_vertex(self):
        return self._start_vertex

    @property
    def end_vertex(self):
        return self._end_vertex

    @property
    def flags(self):
        return self._flags

    @property
    def special_type(self):
        return self._special_type

    @property
    def sector_tag(self):
        return self._sector_tag

    @property
    def right_sidedef(self):
        return self._right_sidedef

    @property
    def left_sidedef(self):
        return self._left_sidedef

    @property
    def is_one_sided(self):
        return self.left_sidedef == -1 or self.right_sidedef == -1

    @staticmethod
    def element_size():
        return 14

