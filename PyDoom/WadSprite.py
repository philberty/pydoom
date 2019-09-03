import struct
import io


class WadPicture:

    def __init__(self, name, width, height, left, top, pixels):
        self._name = name
        self._width = width
        self._height = height
        self._left = left
        self._top = top
        self._pixels = pixels

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def left(self):
        return self._left

    @property
    def top(self):
        return self._top

    @property
    def pixels(self):
        return self._pixels

    @staticmethod
    def pixels_to_rgb_pixels(pixels, palette):
        return tuple(map(lambda r: tuple(map(lambda i: palette[i], r)), pixels))

    def save_jpeg(self, path, palette):
        import pygame
        rgb_pixels = WadPicture.pixels_to_rgb_pixels(self.pixels, palette)

        image = pygame.Surface((self.width, self.height))
        for w in range(self.width):
            for h in range(self.height):
                image.set_at((w, h), rgb_pixels[h][w])

        pygame.image.save(image, path)


class WadSprite:

    def __init__(self, thing, lumps):
        self._thing = thing
        self._lumps = lumps

    @property
    def thing(self):
        return self._thing

    @property
    def lumps(self):
        return self._lumps

    @staticmethod
    def read_sprite_header(lump):
        data = io.BytesIO(lump.data)
        width, \
            height, \
            left, \
            top = struct.unpack("<HHHH", data.read(8))
        return width, height, left, top

    def __len__(self):
        return len(self.lumps)

    def __iter__(self):
        self._iterIndex = 0
        return self

    def __next__(self):
        if self._iterIndex >= len(self):
            raise StopIteration()
        
        index = self._iterIndex
        self._iterIndex += 1
        return self.get_doom_sprite_at_lump_index(index)

    def __getitem__(self, index) -> WadPicture:
        return self.get_doom_sprite_at_lump_index(index)

    def get_doom_sprite_at_lump_index(self, lump_index) -> WadPicture:
        return WadSprite.get_wad_picture_for_lump(self.lumps[lump_index])

    @staticmethod
    def get_wad_picture_for_lump(lump) -> WadPicture:
        width, height, left, top = WadSprite.read_sprite_header(lump)

        buf = io.BytesIO(lump.data)
        buf.seek(8)  # offset from header

        column_array = tuple(map(lambda c: struct.unpack("<I", buf.read(4))[0],
                                 range(width)))

        pixel_data = list(map(lambda h: None, range(height)))
        for i in range(len(pixel_data)):
            pixel_data[i] = list(map(lambda p: 0, range(width)))

        for i in range(width):
            buf.seek(column_array[i])

            rowstart = 0
            while rowstart != 255:
                rowstart = struct.unpack("<B", buf.read(1))[0]
                if rowstart == 255:
                    break

                pixel_count = struct.unpack("<B", buf.read(1))[0]
                dummy_value = struct.unpack("<B", buf.read(1))[0]

                for j in range(pixel_count):
                    pixel = struct.unpack("<B", buf.read(1))[0]

                    # write Pixel to image, j + rowstart = row, i = column
                    row = j + rowstart
                    column = i
                    pixel_data[row][column] = pixel

                dummy_value = struct.unpack("<B", buf.read(1))[0]

        return WadPicture(lump.name, width, height, left, top, pixel_data)

