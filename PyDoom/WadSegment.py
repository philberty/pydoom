from PyDoom.WadElement import WadElement

import struct


class WadSegment(WadElement):

    """
    http://doom.wikia.com/wiki/Seg
    """

    _start_vertex = None
    _end_vertex = None
    _angle = None
    _linedef_index = None
    _side = None
    _offset = None

    def __init__(self, chunk):
        super(WadSegment, self).__init__()
        self._start_vertex, \
            self._end_vertex, \
            self._angle, \
            self._linedef_index, \
            self._side, \
            self._offset = struct.unpack("<hhhhhh", chunk)

    @property
    def start_vertex(self):
        return self._start_vertex

    @property
    def end_vertex(self):
        return self._end_vertex

    @property
    def angle(self):
        return self._angle

    @property
    def linedef_index(self):
        return self._linedef_index

    @property
    def side(self):
        return self._side

    @property
    def offset(self):
        return self._offset

    @staticmethod
    def element_size():
        return 12
