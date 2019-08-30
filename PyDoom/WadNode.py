from PyDoom.WadElement import WadElement

import struct


class WadNode(WadElement):

    """
    http://doom.wikia.com/wiki/Node
    """

    NF_SUBSECTOR = 0x8000

    _partition_x = None
    _partition_y = None
    _delta_x = None
    _delta_y = None
    _right_bounding_box = None
    _left_bounding_box = None
    _children = None

    def __init__(self, chunk):
        super(WadNode, self).__init__()
        self._partition_x, \
            self._partition_y, \
            self._delta_x, \
            self._delta_y, = struct.unpack("<hhhh", chunk[0:8])
        self._right_bounding_box = struct.unpack("<hhhh", chunk[8:16])
        self._left_bounding_box = struct.unpack("<hhhh", chunk[16:24])
        self._children = struct.unpack("<hh", chunk[24:28])

    @property
    def partiton_x(self):
        return self._partition_x

    @property
    def partition_y(self):
        return self._partition_y

    @property
    def delta_x(self):
        return self._delta_x

    @property
    def delta_y(self):
        return self._delta_y

    @property
    def right_bounding_box(self):
        return self._right_bounding_box

    @property
    def left_bounding_box(self):
        return self._left_bounding_box

    @property
    def children(self):
        return self._children

    @staticmethod
    def element_size():
        return 28

    def __repr__(self):
        return "WadNode: x {0} y {1} dx {2} dy {3} rbbox {4} lbbox {5} children {6}".format(self._partition_x,
                                                                                   self._partition_y,
                                                                                   self._delta_x,
                                                                                   self._delta_y,
                                                                                   self._right_bounding_box,
                                                                                   self._left_bounding_box,
                                                                                   self._children)
