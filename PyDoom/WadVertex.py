from PyDoom.WadElement import WadElement

import struct


class WadVertex(WadElement):

    """
    http://doom.wikia.com/wiki/Vertex
    """

    _x = None
    _y = None

    def __init__(self, chunk):
        super(WadVertex, self).__init__()
        self._x, self._y = struct.unpack("<hh", chunk)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @staticmethod
    def element_size():
        return 4

    def __repr__(self):
        return "WadVertex {{0},{1}}".format(self.x, self.y)
