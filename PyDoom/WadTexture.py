from PyDoom.WadDirectory import WadDirectory
from PyDoom.WadElement import WadElement
from PyDoom.WadPnames import WadPnames

from typing import Tuple

import struct


class WadPatch:

    _patch = None
    _patch_name = None
    _patch_lump = None

    def __init__(self, directory: WadDirectory, offset: int):
        self._x = struct.unpack("<h", directory.data[offset:offset + 0x02])[0]
        self._y = struct.unpack("<h", directory.data[offset + 0x02:offset + 0x04])[0]
        self._patch_index = struct.unpack("<h", directory.data[offset + 0x04:offset + 0x06])[0]
        self._step_dir = struct.unpack("<h", directory.data[offset + 0x06:offset + 0x08])[0]
        self._colormap = struct.unpack("<h", directory.data[offset + 0x08:offset + 0x0A])[0]

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def patch_name(self) -> int:
        return self._patch_name

    @property
    def patch_index(self) -> int:
        return self._patch_index

    @property
    def patch_lump(self):
        return self._patch_lump

    @property
    def step_dir(self) -> int:
        return self._step_dir

    @property
    def colormap(self) -> int:
        return self._colormap

    def compile_with_pnames(self, pnames: WadPnames):
        self._patch_name = pnames.patches[self.patch_index]

    def compile_with_lumps(self, wad):
        self._patch_lump = wad[self.patch_name][0]


class WadMapTexture:

    def __init__(self, directory: WadDirectory, offset: int):
        self._name = directory.data[offset:offset + 0x08].decode('utf-8').rstrip('\0')
        self._masked = True if struct.unpack("<l", directory.data[offset + 0x08:offset + 0x0C])[0] == 1 else False
        self._width = struct.unpack("<h", directory.data[offset + 0x0C:offset + 0x0E])[0]
        self._height = struct.unpack("<h", directory.data[offset + 0x0E:offset + 0x10])[0]
        self._column_directory = struct.unpack("<l", directory.data[offset + 0x10:offset + 0x14])[0]
        self._patch_count = struct.unpack("<h", directory.data[offset + 0x14:offset + 0x16])[0]
        self._patches = tuple(map(lambda i: WadPatch(directory, offset + 0x16), range(1, self.patch_count)))

    @property
    def name(self) -> str:
        return self._name

    @property
    def masked(self) -> bool:
        return self._masked

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def column_directory(self) -> int:
        return self._column_directory

    @property
    def patch_count(self) -> int:
        return self._patch_count

    @property
    def patches(self) -> Tuple[WadPatch]:
        return self._patches

    def compile_with_pnames(self, pnames: WadPnames):
        for i in self.patches:
            i.compile_with_pnames(pnames)

    def compile_with_lumps(self, wad):
        for i in self.patches:
            i.compile_with_lumps(wad)


class WadTexture(WadElement):
    """
    https://doom.fandom.com/wiki/TEXTURE1_and_TEXTURE2
    """

    def __init__(self, directory: WadDirectory):
        super(WadTexture, self).__init__()
        self._num_textures = struct.unpack("<l", directory.data[0:4])[0]
        self._texture_offsets = tuple(
            map(lambda i: struct.unpack("<l", directory.data[4 + ((i - 1) * 4):4 + (i * 4)])[0],
                range(1, self._num_textures + 1)))
        self._textures = tuple(map(lambda offset: WadMapTexture(directory, offset), self.texture_offsets))
        self._texture_map = {}
        for i in self._textures:
            self._texture_map[i.name] = i

    @property
    def num_textures(self) -> int:
        return self._num_textures

    @property
    def texture_offsets(self):
        return self._texture_offsets

    @property
    def textures(self) -> Tuple[WadMapTexture]:
        return self._textures

    def contains_texture(self, name):
        return name in self._texture_map

    def get_texture(self, item):
        return self._texture_map[item]

    def __getitem__(self, item):
        return self.get_texture(item)

    def compile_with_pnames(self, pnames: WadPnames):
        for i in self.textures:
            i.compile_with_pnames(pnames)

    def compile_with_lumps(self, wad):
        for i in self.textures:
            i.compile_with_lumps(wad)
