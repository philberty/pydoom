from PyDoom.Definitions import LineDef, SlopeType, BoxPositions, LineSeg, SideDef, Sector
from PyDoom.WadLinedef import WadLinedef
from PyDoom.WadThing import WadThing
from PyDoom.WadSidedef import WadSidedef
from PyDoom.WadVertex import WadVertex
from PyDoom.WadSegment import WadSegment
from PyDoom.WadSubSector import WadSubSector
from PyDoom.WadSector import WadSector
from PyDoom.WadNode import WadNode
from PyDoom import LOG

from typing import List


class WadLevel:
    ## Fields

    _name = None
    _things = None
    _linedefs = None
    _sidedefs = None
    _vertexes = None
    _segs = None
    _ssectors = None
    _nodes = None
    _sectors = None
    _reject = None
    _blockmap = None
    _wad = None

    ## Constructor

    def __init__(self, name, things, linedefs, sidedefs, vertexes, segs, ssectors, nodes, sectors, reject, blockmap,
                 wad):
        self._name = name
        self._wad = wad

        # load lumps into relevant classes
        self._things = self._load_lump(things, WadThing, wad)
        self._linedefs = self._load_lump(linedefs, WadLinedef)
        self._sidedefs = self._load_lump(sidedefs, WadSidedef)
        self._vertexes = self._load_lump(vertexes, WadVertex)
        self._segs = self._load_lump(segs, WadSegment)
        self._ssectors = self._load_lump(ssectors, WadSubSector)
        self._sectors = self._load_lump(sectors, WadSector)
        self._nodes = self._load_lump(nodes, WadNode)

        # find lower left
        self.lower_left = (min((v.x for v in self.vertices)), min((v.y for v in self.vertices)))
        # find upper right
        self.upper_right = (max((v.x for v in self.vertices)), max((v.y for v in self.vertices)))
        # find shift
        self.shift = (0 - self.lower_left[0], 0 - self.lower_left[1])

        LOG.info("found lower left: {0}".format(self.lower_left))
        LOG.info("found upper right: {0}".format(self.upper_right))
        LOG.info("found shift: {0}".format(self.shift))

    ## Properties

    @property
    def log(self):
        return LOG

    @property
    def name(self) -> str:
        return self._name

    @property
    def things(self) -> List[WadThing]:
        return self._things

    @property
    def linedefs(self) -> List[WadLinedef]:
        return self._linedefs

    @property
    def sidedefs(self) -> List[WadSidedef]:
        return self._sidedefs

    @property
    def vertices(self) -> List[WadVertex]:
        return self._vertexes

    @property
    def segs(self) -> List[WadSegment]:
        return self._segs

    @property
    def sub_sectors(self) -> List[WadSubSector]:
        return self._ssectors

    @property
    def nodes(self) -> List[WadNode]:
        return self._nodes

    @property
    def root_node(self):
        # root node is always the last one
        return self.nodes[-1]

    @property
    def sectors(self):
        return self._sectors

    @property
    def reject(self):
        return self._reject

    @property
    def blockmap(self):
        return self._blockmap

    ## Methods

    def find_first_thing_by_name(self, thing_name):
        entities = tuple(filter(lambda t: t.definition.name == thing_name, self.things))
        if len(entities) == 0:
            raise Exception('unable to find [{0}] thing'.format(thing_name))

        return entities[0]

    def _load_lump_elements(self, lump, element_size):
        elements = []
        data = lump.data
        number_of_elements = int(lump.size / element_size)
        for i in range(number_of_elements):
            chunk = data[i * element_size: (i + 1) * element_size]
            elements.append(chunk)
        return elements

    def _load_lump(self, lump, container, *args):
        elements = self._load_lump_elements(lump, container.element_size())
        return list(map(lambda chunk: container(chunk, *args), elements))

    def normalize(self, point):
        return self.shift[0] + point[0], self.shift[1] + point[1]

    def save_svg(self, path):
        import svgwrite

        # borrowed from https://gist.github.com/jasonsperske/42284303cf6a7ef19dc3

        view_box_size = self.normalize(self.upper_right)
        if view_box_size[0] > view_box_size[1]:
            canvas_size = (1024, int(1024 * (float(view_box_size[1]) / view_box_size[0])))
        else:
            canvas_size = (int(1024 * (float(view_box_size[0]) / view_box_size[1])), 1024)

        dwg = svgwrite.Drawing(path, profile='tiny', size=canvas_size, viewBox=('0 0 %d %d' % view_box_size))
        for line in self.linedefs:
            start = self.vertices[line.start_vertex]
            end = self.vertices[line.end_vertex]
            a = self.normalize((start.x, start.y))
            b = self.normalize((end.x, end.y))
            if line.is_one_sided:
                dwg.add(dwg.line(a, b, stroke='#333', stroke_width=10))
            else:
                dwg.add(dwg.line(a, b, stroke='#999', stroke_width=3))
        dwg.save()

    def compile_level(self):
        sectors = list(map(self.compile_sectors, self.sectors))
        sides = list(map(lambda s: self.compile_side_defs(s, sectors), self.sidedefs))
        lines = list(map(lambda i: self.compile_line_def(i, sides), self.linedefs))
        segs = list(map(lambda s: self.compile_seg(s, lines, sides), self.segs))

        return sectors, sides, lines, segs

    def compile_sectors(self, wad_sector: WadSector) -> Sector:
        sector = Sector()

        sector.floor_height = wad_sector.floor_height
        sector.ceiling_height = wad_sector.ceiling_height
        sector.floor_pic = None  # TODO - R_FlatNumForName
        sector.ceiling_pic = None  # TODO - R_FlatNumForName
        sector.light_level = wad_sector.light_level
        sector.special = wad_sector.sector_type
        sector.tag = wad_sector.tag_number
        sector.thing_list = None

        return sector

    def compile_side_defs(self, wad_side_def: WadSidedef, sectors: List[Sector]) -> SideDef:
        side = SideDef()

        side.texture_offset = wad_side_def.x_offset
        side.row_offset = wad_side_def.y_offset

        self.log.debug("top_texture [{0}]".format(wad_side_def.name_of_upper_texture))
        self.log.debug("mid_texture [{0}]".format(wad_side_def.name_of_middle_texture))
        self.log.debug("bottom_texture [{0}]".format(wad_side_def.name_of_lower_texture))

        side.top_texture = self._wad.lookup_texture(wad_side_def.name_of_upper_texture)
        side.mid_texture = self._wad.lookup_texture(wad_side_def.name_of_middle_texture)
        side.bottom_texture = self._wad.lookup_texture(wad_side_def.name_of_lower_texture)

        print("top:", side.top_texture)
        print("mid:", side.mid_texture)
        print("bottom:", side.bottom_texture)

        side.sector = sectors[wad_side_def.sector_index]

        return side

    def compile_line_def(self, wad_line_def: WadLinedef, sides: List[SideDef]) -> LineDef:
        line = LineDef()

        line.flags = wad_line_def.flags
        line.special = wad_line_def.special_type
        line.tag = wad_line_def.sector_tag
        line.v1 = self.vertices[wad_line_def.start_vertex]
        line.v2 = self.vertices[wad_line_def.end_vertex]
        line.dx = line.v2.x - line.v1.x
        line.dy = line.v2.y - line.v2.y

        if line.dx <= 0:
            line.slope_type = SlopeType.ST_VERTICAL
        elif line.dy <= 0:
            line.slope_type = SlopeType.ST_HORIZONTAL
        elif (line.dy / line.dx) > 0:
            line.slope_type = SlopeType.ST_POSITIVE
        else:
            line.slope_type = SlopeType.ST_NEGATIVE

        if line.v1.x < line.v2.x:
            line.bbox[BoxPositions.BOXLEFT] = line.v1.x
            line.bbox[BoxPositions.BOXRIGHT] = line.v2.x
        else:
            line.bbox[BoxPositions.BOXLEFT] = line.v2.x
            line.bbox[BoxPositions.BOXRIGHT] = line.v1.x

        if line.v1.y < line.v2.y:
            line.bbox[BoxPositions.BOXBOTTOM] = line.v1.y
            line.bbox[BoxPositions.BOXTOP] = line.v2.y
        else:
            line.bbox[BoxPositions.BOXBOTTOM] = line.v2.y
            line.bbox[BoxPositions.BOXTOP] = line.v1.y

        line.side_num[0] = wad_line_def.right_sidedef
        line.side_num[1] = wad_line_def.left_sidedef

        if line.side_num[0] != -1:
            line.front_sector = sides[wad_line_def.right_sidedef].sector
        else:
            line.front_sector = None

        if line.side_num[1] != -1:
            line.back_sector = sides[wad_line_def.left_sidedef].sector
        else:
            line.back_sector = None

        return line

    def compile_seg(self, seg: WadSegment, lines: List[LineDef], sides: List[SideDef]) -> LineSeg:
        s = LineSeg()

        s.v1 = self.vertices[seg.start_vertex]
        s.v2 = self.vertices[seg.end_vertex]
        s.angle = seg.angle
        s.offset = seg.offset
        s.line = lines[seg.linedef_index]
        s.side = sides[seg.side]
        s.front_sector = sides[s.line.side_num[seg.side]].sector

        # ML_TWOSIDED 4
        if (s.line.flags & 4) > 0:
            s.back_sector = sides[s.line.side_num[seg.side ^ 1]].sector
        else:
            s.back_sector = None

        return s
