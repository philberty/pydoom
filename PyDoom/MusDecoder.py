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

        self.write_midi_header(self._decode_buffer)

        # BODY

        self.write_midi_trailer(self._decode_buffer)

        return self._decode_buffer

    def write_midi_header(self, buffer):
        for i in ['M', 'T', 'h', 'd']:
            buffer.append(ord(i))

        # header
        out = struct.pack(">I", 6)
        buffer += out

        # Format(single track).
        out = struct.pack(">H", 0)
        buffer += out

        # Number of tracks.
        out = struct.pack(">H", 1)
        buffer += out

        # Delta ticks per quarter note(140).
        out = struct.pack(">H", 140)
        buffer += out

        # Track header.
        for i in ['M', 'T', 'r', 'k']:
            buffer.append(ord(i))

        # Length of the track in bytes.
        self._track_size_offset = len(buffer)
        out = struct.pack(">I", 0) # updated later
        buffer += out

        # The first MIDI ev sets the tempo.
        buffer += 0     # No delta ticks
        buffer += 0xff
        buffer += 0x51
        buffer += 3
        buffer += 0xf   # Exactly one second per quarter note.
        buffer += 0x42
        buffer += 0x40


    def write_midi_trailer(self, buffer):
        # End of track.
        buffer += 0
        buffer += 0xff
        buffer += 0x2f
        buffer += 0

        # All the MIDI data has now been written. Update the track length.
        track_size = len(buffer) - self._track_size_offset - 4
        out.setOffset(trackSizeOffset)
        out << trackSize;

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
