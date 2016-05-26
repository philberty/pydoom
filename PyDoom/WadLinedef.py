from PyDoom.WadElement import WadElement

import struct


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

