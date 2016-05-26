from PyDoom.WadLinedef import WadLinedef
from PyDoom.WadThing import WadThing
from PyDoom.WadSidedef import WadSidedef
from PyDoom.WadVertex import WadVertex
from PyDoom.WadSegment import WadSegment
from PyDoom.WadSubSector import WadSubSector
from PyDoom.WadSector import WadSector
from PyDoom.WadNode import WadNode


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

## Constructor

    def __init__(self, name, things, linedefs, sidedefs, vertexes, segs, ssectors, nodes, sectors, reject, blockmap):
        self._name = name

        # load lumps into relevant classes
        self._things = self._load_lump(things, WadThing)
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

## Properties

    @property
    def name(self):
        return self._name

    @property
    def things(self):
        return self._things

    @property
    def linedefs(self):
        return self._linedefs

    @property
    def sidedefs(self):
        return self._sidedefs

    @property
    def vertices(self):
        return self._vertexes

    @property
    def segs(self):
        return self._segs

    @property
    def ssectors(self):
        return self._ssectors

    @property
    def nodes(self):
        return self._nodes

    @property
    def sectors(self):
        return self._sectors

    @property
    def reject(self):
        return self._reject

    @property
    def blockmap(self):
        return self._blockmap

## Emulation

    def __repr__(self):
        return "Wad Level"

    def __str__(self):
        return "Wad Level: %s" % self._name

## Methods

    def _load_lump_elements(self, lump, element_size):
        elements = []
        data = lump.data
        number_of_elements = int(lump.size / element_size)
        for i in range(number_of_elements):
            chunk = data[i * element_size: (i + 1) * element_size]
            elements.append(chunk)
        return elements

    def _load_lump(self, lump, container):
        elements = self._load_lump_elements(lump, container.element_size())
        return list(map(lambda chunk: container(chunk), elements))

    def _normalize(self, point):
        return self.shift[0] + point[0], self.shift[1] + point[1]

    def save_svg(self):
        import svgwrite

        # borrowed from https://gist.github.com/jasonsperske/42284303cf6a7ef19dc3

        view_box_size = self._normalize(self.upper_right)
        if view_box_size[0] > view_box_size[1]:
            canvas_size = (1024, int(1024*(float(view_box_size[1]) / view_box_size[0])))
        else:
            canvas_size = (int(1024*(float(view_box_size[0]) / view_box_size[1])), 1024)

        dwg = svgwrite.Drawing(self.name+'.svg', profile='tiny', size=canvas_size , viewBox=('0 0 %d %d' % view_box_size))
        for line in self.linedefs:
            start = self.vertices[line.start_vertex]
            end = self.vertices[line.end_vertex]
            a = self._normalize((start.x, start.y))
            b = self._normalize((end.x, end.y))
            if line.is_one_sided():
                dwg.add(dwg.line(a, b, stroke='#333', stroke_width=10))
            else:
                dwg.add(dwg.line(a, b, stroke='#999', stroke_width=3))
        dwg.save()
