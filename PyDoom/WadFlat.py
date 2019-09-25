import io
import struct

from PyDoom import WadDirectory
from PyDoom.WadSprite import WadPicture


class WadFlat:

    @staticmethod
    def parse(lump: WadDirectory) -> WadPicture:
        data = io.BytesIO(lump.data)
        pixels = []
        for i in range(64):
            pixels.append(struct.unpack("<BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
                                        data.read(64)))
        return WadPicture(lump.name, 64, 64, 0, 0, pixels)

