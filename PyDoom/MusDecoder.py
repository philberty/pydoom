from PyDoom.WadException import WadException
from PyDoom import LOG as logger

import tempfile
import struct
import ctypes
import io


# kindly ported from https://github.com/skyjake/Doomsday-Engine
# m_mus2midi.cpp

# https://github.com/kripken/boon/blob/master/src/mmus2mid.c



class MusDecoder:

    _lump = None
    _buffer = None
    _decode_buffer = None
    _header = None
    _track_size_offset = None

    def __init__(self, lump):
        self._lump = lump
        self._buffer = io.BytesIO(lump.data)
        self._decode_buffer = bytearray()

    def decode(self):
        self._header = MusDecoder.parse_header(self._lump)
        print(self._header)



        return self._decode_buffer

    @staticmethod
    def decode_mus_to_midi(lump):
        decoder = MusDecoder(lump)
        return decoder.decode()

    @staticmethod
    def parse_header(lump):
        data = io.BytesIO(lump.data)
        identifier = struct.unpack("<4s", data.read(4))[0].decode("ascii")

        score_length, \
            score_start, \
            channels, \
            sec_channels, \
            instrument_count, \
            padding = struct.unpack("<HHHHHH", data.read(12))

        if not identifier.startswith("MUS"):
            raise WadException("Invalid mus header found [%s]" % identifier)

        return {
            "identifier": identifier,
            "score_length": score_length,
            "score_start": score_start,
            "channels": channels,
            "sec_channels": sec_channels,
            "instrument_count": instrument_count,
            "padding": padding
        }
