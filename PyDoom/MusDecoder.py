from PyDoom.WadException import WadException
from PyDoom import LOG as logger

import tempfile
import struct
import ctypes
import io


# kindly ported from https://github.com/skyjake/Doomsday-Engine
# m_mus2midi.cpp

# https://github.com/kripken/boon/blob/master/src/mmus2mid.c


class MusEvent:

    RELEASE_NOTE = 0
    PLAY_NOTE = 1
    PITCH_WHEEL = 2
    SYSTEM = 3
    CONTROLLER = 4
    FIVE = 5
    SCORE_END = 6
    SEVEN = 7


class MusControllers:

    INSTRUMENT = 0
    BANK = 1
    MODULATION = 2
    VOLUME = 3
    PAN = 4
    EXPRESSION = 5
    REVERB = 6
    CHOROUS = 7
    SUSTAIN_PEDAL = 8
    SOFT_PEDAL = 9

    # VALUELESS CONTROLLERS
    
    SOUNDS_OFF = 10
    NOTES_OFF = 11
    MONO = 12
    POLY = 13
    RESET_ALL = 14
    NUM_CTRLS = 15

    
ctrlMus2Midi = [
    0, # Not used.
    0, # Bank select.
    1, # Modulation.
    7, # Volume.
    10, # Pan.
    11, # Expression.
    91, # Reverb.
    93, # Chorus.
    64, # Sustain pedal.
    67, # Soft pedal.
    
    # The valueless controllers:
    120, # All sounds off.
    123, # All notes off.
    126, # Mono.
    127, # Poly.
    121  # Reset all controllers.
]
    

class MusDecoder:

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
        track_size_offset = len(decode_buffer)
        decode_buffer += struct.pack(">i", 0) # updated later on
        
        # The first MIDI ev sets the tempo.
        decode_buffer += struct.pack(">B", 0)  # no delta ticks
        decode_buffer += struct.pack(">B", 0xff)
        decode_buffer += struct.pack(">B", 0x51)
        decode_buffer += struct.pack(">B", 3)
        decode_buffer += struct.pack(">B", 0xf) # Exactly one second per quarter note.
        decode_buffer += struct.pack(">B", 0x42)
        decode_buffer += struct.pack(">B", 0x40)

        # do
        lump_score_start_offset = mus_header['score_start']
        logger.debug(mus_header)

        # read_start from scrore start
        print("length of music lump:", len(lump.data))

        music_buf = io.BytesIO(lump.data)
        music_buf.read(mus_header['score_start'])
        
        channel_volumes = list(map(lambda i: 64, range(16)))

        ## -------

        def get_next_event(read_time, buf):

            # midi event result
            event = {
                'deltaTime': read_time,
                'command': 0,
                'size': 0,
                'params': [0x0, 0x0]
            }
            
            read_time = 0
            musEvent = struct.unpack("<B", buf.read(1))[0]

            channel = ctypes.c_uint8(musEvent & 0x80).value
            ev = ctypes.c_uint8((musEvent & 0x7f) >> 4).value
            last = ctypes.c_uint8(musEvent & 0x0f).value

            if channel > len(channel_volumes):
                channel = 0
            
            # raw mus event
            eventDesc = {
                'channel': channel,
                'ev': ev,
                'last': last
            }

            print(eventDesc)

            if eventDesc['ev'] == MusEvent.PLAY_NOTE:
                event['command'] = 0x90
                event['size'] = 2
                
                event['params'][0] = struct.unpack("<B", buf.read(1))[0]

                if ctypes.c_uint8(event['params'][0] & 0x80).value:
                    channel_volumes[eventDesc['channel']] = struct.unpack("<B", buf.read(1))[0]

                event['params'][0] = ctypes.c_uint8(event['params'][0] & 0x7f).value

                i = channel_volumes[eventDesc['channel']]
                if i > 127:
                    i = 127
                
                event['params'][1] = i

            elif eventDesc['ev'] == MusEvent.RELEASE_NOTE:
                event['command'] = 0x80
                event['size'] = 2
                # which note??
                event['params'][0] = struct.unpack("<B", buf.read(1))[0]

            elif eventDesc['ev'] == MusEvent.CONTROLLER:
                event['command'] = 0xb0
                event['size'] = 2
                event['params'][0] = struct.unpack("<B", buf.read(1))[0]
                event['params'][1] = struct.unpack("<B", buf.read(1))[0]

                if event['params'][0] == MusControllers.INSTRUMENT:
                    event['command'] = 0xc0
                    event['size'] = 1
                    event['params'][0] = event['params'][1]
                
                else:
                    event['params'][0] = ctrlMus2Midi[event['params'][0]]

            elif eventDesc['ev'] == MusEvent.PITCH_WHEEL:
                event['command'] = 0xe0
                event['size'] = 2
                
                i = struct.unpack("<B", buf.read(1))[0]
                i = ctypes.c_uint8(i << 6).value
                
                event['params'][0] = ctypes.c_uint8(i & 0x7f).value
                event['params'][1] = ctypes.c_uint8(i >> 7).value

            elif eventDesc['ev'] == MusEvent.SYSTEM:
                event['command'] = 0xb0
                event['size'] = 2
                
                i = struct.unpack("<B", buf.read(1))[0]
                event['params'][0] = ctrlMus2Midi[i]

            elif eventDesc['ev'] == MusEvent.SCORE_END:
                logger.warn("SCORE_END")
                return False

            else:
                logger.warn("invalid mus format")
                return False

            # choose channel
            i = eventDesc['channel']

            # redirect mus channel 16 to midid channel 10 percussion
            if i == 15:
                i = 9
            elif i == 9:
                i = 15
            
            event['command'] = ctypes.c_uint8(event['command'] | i).value

            # check if this was the last event in a group
            if ctypes.c_uint8(~eventDesc['last']).value:
                return (True, event, read_time)

            read_time = 0

            i = struct.unpack("<B", buf.read(1))[0]
            x = ctypes.c_uint8(i & 0x7f).value
            read_time = ctypes.c_int((read_time << 7) + x)

            while (ctypes.c_uint8(i & 0x80)).value:
                i = struct.unpack("<B", buf.read(1))[0]
                x = ctypes.c_uint8(i & 0x7f).value
                read_time = ctypes.c_int((read_time << 7) + x)

            return (True, event, read_time)
        
        ## -------

        read_time = 0
        
        while True:
            ok = get_next_event(read_time, music_buf)
            if ok is False:
                break

            ok, event, read_time = ok

            if event['deltaTime'] == 0:
                decode_buffer += struct.pack(">B", 0)
                
            else:

                b = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                i = -1
                while event['deltaTime'] > 0:
                    b[i] = ctypes.c_uint8(event['deltaTime'] & 0x7f)
                    i += 1
                    if i > 0:
                        b[i] = ctypes.c_uint8(b[i] | 0x80).value
                    
                    event['deltaTime'] = ctypes.c_uint8(event['deltaTime'] >> 7).value

                while i >= 0:
                    decode_buffer += struct.pack(">B", b[i])
                    i -= 1

            decode_buffer += struct.pack(">B", event['command'])
            for i in range(event['size']):
                decode_buffer += struct.pack(">B", event['params'][i])
        
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

        return memory_view_buffer
    

    @staticmethod
    def parse_header(lump):
        data = lump.data
        identifier = data[0:4].decode('utf-8').rstrip('\0')
        score_length, \
            score_start, \
            channels, \
            sec_channels, \
            instrument_count, \
            padding = struct.unpack("<hhhhhh", data[4:16])

        if "MUS" not in identifier:
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
