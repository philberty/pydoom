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
    def pixelsToRgbPixels(pixels, palette):
        return tuple(map(lambda r: tuple(map(lambda i: palette[i], r)), pixels))

    def savePng(self, path, palette):
        import png

        pixels = WadPicture.pixelsToRgbPixels(self.pixels, palette)        
        png.from_array(pixels, 'RGB').save(path)


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
    def readSpriteHeader(lump):
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
        return self.getDoomPicture(index)

    def getDoomPicture(self, lumpIndex):
        lump = self.lumps[lumpIndex]
        width, height, left, top = WadSprite.readSpriteHeader(lump)

        buf = io.BytesIO(lump.data)
        buf.seek(8) # offset from header
 
        column_array = tuple(map(lambda i: struct.unpack("<I", buf.read(4))[0],
                                 range(width)))

        pixelData = list(map(lambda i: None, range(height)))
        for i in range(len(pixelData)):
            pixelData[i] = list(map(lambda i: 0, range(width)))
        
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
                    pixelData[row][column] = pixel

                dummy_value = struct.unpack("<B", buf.read(1))[0]
        
        return WadPicture(lump.name, width, height, left, top, pixelData)

