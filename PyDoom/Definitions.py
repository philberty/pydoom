from typing import Tuple


class SlopeType:
    ST_HORIZONTAL = 0
    ST_VERTICAL = 1
    ST_POSITIVE = 2
    ST_NEGATIVE = 3


class BoxPositions:
    BOXTOP = 0
    BOXBOTTOM = 1
    BOXLEFT = 2
    BOXRIGHT = 3


class Vertex:
    _x = None
    _y = None

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def raw(self) -> Tuple[int, int]:
        return self._x, self._y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self,value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def __repr__(self):
        return "Vertex {0},{1}".format(self.x, self.y)


class LineDef:

    # Vertices, from v1 to v2.
    v1 = None
    v2 = None

    # recalculated v2 - v1 for side checking.
    dx = None
    dy = None

    # Animation related.
    flags = None
    special = None
    tag = None

    # Visual appearance: SideDefs.
    # sidenum[1] will be -1 if one sided
    side_num = [None, None]

    # Neat. Another bounding box, for the extent of the LineDef
    bbox = [None, None, None, None]

    # To aid move clipping.
    slope_type = None

    # Front and back sector.
    # Note: redundant? Can be retrieved from SideDefs.
    front_sector = None
    back_sector = None

    # if == validcount, already checked
    valid_count = None

    # thinkert for reversable actions
    special_data = None


class SideDef:

    # add this to the calculated texture column
    texture_offset = None

    # add this to the calculated texture top
    row_offset = None

    # Texture indices. We do not maintain names here.
    top_texture = None
    bottom_texture = None
    mid_texture = None

    # Sector the SideDef is facing.
    sector = None


class Sector:

    floor_height = None
    ceiling_height = None
    floor_pic = None
    ceiling_pic = None
    light_level = None
    special = None
    tag = None

    # 0 = untraversed, 1,2 = sndlines -1
    sound_traversed = None

    # thing that made a sound (or null)
    sound_target = None

    # mapblock bounding box for height changes
    block_box = None

    # origin for any sounds played by the sector
    sound_orgin = None

    # if == validcount, already checked
    valid_count = None

    # list of mobjs in sector
    thing_list = None

    # thinkert for reversable actions
    special_data = None


class LineSeg:

    v1 = None
    v2 = None
    offset = None
    angle = None
    side = None
    line = None

    # Sector references. Could be retrieved from linedef, too. backsector is NULL for one sided lines
    front_sector = None
    back_sector = None

    def __repr__(self):
        return "CompiledLineSeg: v1: {0} v2: {1} offset: {2} angle: {3} side: {4} line: {5}".format(self.v1, self.v2,
                                                                                                   self.offset,
                                                                                                   self.angle,
                                                                                                   self.side, self.line)
