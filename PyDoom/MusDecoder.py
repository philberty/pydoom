from PyDoom.WadException import WadException

import tempfile
import struct


class MusDecoder(object):

    @staticmethod
    def decode_mus_to_midi(lump):
        mus_header = MusDecoder.parse_header(lump)
        decode_buffer = b''

        # Start with the MIDI header.
        decode_buffer += struct.pack(">BBBB", ord('M'), ord('T'), ord('h'), ord('d'))
        # Header size.
        decode_buffer += struct.pack(">i", 6)
        # Format (single track).
        decode_buffer += struct.pack(">h", 0)
        # Number of tracks.
        decode_buffer += struct.pack(">h", 1)
        # Delta ticks per quarter note (140).
        decode_buffer += struct.pack(">h", 140)
        # Track header.
        decode_buffer += struct.pack(">BBBB", ord('M'), ord('T'), ord('r'), ord('k'))
        # Length of the track in bytes.
        track_size_offset = 18
        decode_buffer += struct.pack(">i", 0) # updated later on
        
        # The first MIDI ev sets the tempo.
        decode_buffer += struct.pack(">B", 0)
        decode_buffer += struct.pack(">B", 0xff)
        decode_buffer += struct.pack(">B", 0x51)
        decode_buffer += struct.pack(">B", 3)
        decode_buffer += struct.pack(">B", 0xf)
        decode_buffer += struct.pack(">B", 0x42)
        decode_buffer += struct.pack(">B", 0x40)

        # do
        lump_score_start_offset = mus_header['score_start']
        print(lump_score_start_offset)

        
        
        # done

        decode_buffer += struct.pack(">B", 0)
        decode_buffer += struct.pack(">B", 0xff)
        decode_buffer += struct.pack(">B", 0x2f)
        decode_buffer += struct.pack(">B", 0)

        # fix track size
        memory_view_buffer = bytearray(decode_buffer)
        track_size = len(decode_buffer) - track_size_offset - 4
        fixed_track_size = struct.pack(">i", track_size)
        for i in range(len(fixed_track_size)):
            memory_view_buffer[track_size_offset + i] = fixed_track_size[i]
        
        # write to file
        path = './test.mid'
        with open(path, 'wb') as fd:
            fd.write(memory_view_buffer)
        return path
    

    @staticmethod
    def parse_header(lump):
        data = lump.data
        identifier = data[0:4].decode('utf-8').rstrip('\0')
        score_length, \
            score_start, \
            channels, \
            sec_channels, \
            instrument_count, \
            dummy = struct.unpack("<hhhhhh", data[4:16])

        if "MUS" not in identifier:
            raise WadException("Invalid mus header found [%s]" % identifier)

        return {
            "identifier": identifier,
            "score_length": score_length,
            "score_start": score_start,
            "channels": channels,
            "sec_channels": sec_channels,
            "instrument_count": instrument_count,
            "dummy": dummy
        }
