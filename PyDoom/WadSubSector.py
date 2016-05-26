from PyDoom.WadElement import WadElement

import struct


class WadSubSector(WadElement):

    """
    http://doom.wikia.com/wiki/Subsector
    """

    _segment_count = None
    _first_segment_index = None

    def __init__(self, chunk):
        super(WadSubSector, self).__init__()
        self._segment_count, self._first_segment_index = struct.unpack("<hh", chunk)

    @property
    def segment_count(self):
        return self._segment_count

    @property
    def first_segment_index(self):
        return self._first_segment_index

    @staticmethod
    def element_size():
        return 4
