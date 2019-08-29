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

    def write_midi_header(self, output_buffer):
        for i in ['M', 'T', 'h', 'd']:
            output_buffer.append(ord(i))

        # header
        out = struct.pack(">I", 6)
        output_buffer += out

        # Format(single track).
        out = struct.pack(">H", 0)
        output_buffer += out

        # Number of tracks.
        out = struct.pack(">H", 1)
        output_buffer += out

        # Delta ticks per quarter note(140).
        out = struct.pack(">H", 140)
        output_buffer += out

        # Track header.
        for i in ['M', 'T', 'r', 'k']:
            output_buffer.append(ord(i))

        # Length of the track in bytes.
        self._track_size_offset = len(output_buffer)
        out = struct.pack(">I", 0) # updated later
        output_buffer += out

        # The first MIDI ev sets the tempo.
        output_buffer += struct.pack('>B', 0)    # No delta ticks
        output_buffer += struct.pack('>B', 0xff)
        output_buffer += struct.pack('>B', 0x51)
        output_buffer += struct.pack('>B', 0)
        output_buffer += struct.pack('>B', 0)
        output_buffer += struct.pack('>B', 0)
        output_buffer += struct.pack('>B', 0)
        
        output_buffer += 0xff
        output_buffer += 0x51
        output_buffer += 3
        output_buffer += 0xf   # Exactly one second per quarter note.
        output_buffer += 0x42
        output_buffer += 0x40


    def write_midi_trailer(self, output_buffer):
        # End of track.
        output_buffer += 0
        output_buffer += 0xff
        output_buffer += 0x2f
        output_buffer += 0

        # All the MIDI data has now been written. Update the track length.
        track_size = len(output_buffer) - self._track_size_offset - 4
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
