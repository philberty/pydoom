from PyDoom.WadException import WadException

import struct


class MusDecoder:

    @staticmethod
    def decode_mus_to_midi(lump):
        buffer = b''
        #struct.pack_into("IIh", buffer, 0, 0x4d546864, 6, 0)
        header = MusDecoder.parse_header(lump)
        print(header)
        return buffer

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
