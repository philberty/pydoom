from PyDoom.WadException import WadException

import tempfile
import struct


class MusDecoder:

    @staticmethod
    def decode_mus_to_midi(lump):                
        decode_buffer = b''

        # Start with the MIDI header.
        struct.pack_into(">BBBB", decode_buffer, 0, "MThd")
        
        # Header size.
        struct.pack_into(">i", decode_buffer, 4, 6)
        
        # Format (single track).
        struct.pack_into(">h", decode_buffer, 8, 0)
        
        # Number of tracks.
        struct.pack_into(">h", decode_buffer, 10, 1)
        
        # Delta ticks per quarter note (140).
        struct.pack_into(">h", decode_buffer, 12, 140)
        
        # Track header.
        struct.pack_into(">BBBB", decode_buffer, 14, "MTrk")
        
        # Length of the track in bytes.
        track_size_offset = 18
        struct.pack_into(">i", decode_buffer, 18, 0) # updated later on
        
        # The first MIDI ev sets the tempo.
        struct.pack_into(">B", decode_buffer, 22, 0)
        struct.pack_into(">B", decode_buffer, 23, 0xff)
        struct.pack_into(">B", decode_buffer, 24, 0x51)
        struct.pack_into(">B", decode_buffer, 25, 3)
        struct.pack_into(">B", decode_buffer, 26, 0xf)
        struct.pack_into(">B", decode_buffer, 27, 0x42)
        struct.pack_into(">B", decode_buffer, 28, 0x40)

        
        
        # write to file
        _, decoded_file_path = tempfile.mkstemp()
        with open(decoded_file_path, 'rb') as fd:
            fd.write(decode_buffer)
        
        return decoded_file_path

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
            "channels": channels,
            "sec_channels": sec_channels,
            "instrument_count": instrument_count,
            "dummy": dummy
        }
