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

# (1)  X coordinate of partition line's start
# (2)  Y coordinate of partition line's start
# (3)  DX, change in X to end of partition line
# (4)  DY, change in Y to end of partition line
#
#   If (1) to (4) equaled 64, 128, -64, -64, the partition line would
# go from (64,128) to (0,64).

# (5)  Y upper bound for right bounding-box.\
# (6)  Y lower bound                         All SEGS in right child of node
# (7)  X lower bound                         must be within this box.
# (8)  X upper bound                        /
# (9)  Y upper bound for left bounding box. \
# (10) Y lower bound                         All SEGS in left child of node
# (11) X lower bound                         must be within this box.
# (12) X upper bound                        /
# (13) a NODE or SSECTOR number for the right child. If bit 15 of this
#        <short> is set, then the rest of the number represents the
#        child SSECTOR. If not, the child is a recursed node.
# (14) a NODE or SSECTOR number for the left child."

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

    @property
    def left_child(self):
        return self.children[1]

    @property
    def right_child(self):
        return self.children[0]

    @property
    def is_sub_sector_right_child(self):
        """
        :returns true if bit 15 is set
        """
        return (self.right_child & WadNode.NF_SUBSECTOR) > 0

    @property
    def is_sub_sector_left_child(self):
        """
        :returns true if bit 15 is set
        """
        return (self.left_child & WadNode.NF_SUBSECTOR) > 0

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
