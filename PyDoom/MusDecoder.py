from PyDoom.WadException import WadException
from PyDoom import LOG as logger

import tempfile
import struct
import ctypes
import io


# kindly ported from https://github.com/skyjake/Doomsday-Engine
# m_mus2midi.cpp

# https://github.com/kripken/boon/blob/master/src/mmus2mid.c

MIDI_TRACKS = 32

# C Major
midikey = [
    ctypes.c_uint8(0x00).value,
    ctypes.c_uint8(0xff).value,
    ctypes.c_uint8(0x59).value,
    ctypes.c_uint8(0x02).value,
    ctypes.c_uint8(0x00).value,
    ctypes.c_uint8(0x00).value
]

# uS/qnote
miditempo = [
    ctypes.c_uint8(0x00).value,
    ctypes.c_uint8(0xff).value,
    ctypes.c_uint8(0x51).value,
    ctypes.c_uint8(0x03).value,
    ctypes.c_uint8(0x09).value,
    ctypes.c_uint8(0xa3).value,
    ctypes.c_uint8(0x1a).value
]

# header (length 6, format 1)
midihdr = [
    ctypes.c_uint8(ord('M')).value,
    ctypes.c_uint8(ord('T')).value,
    ctypes.c_uint8(ord('h')).value,
    ctypes.c_uint8(ord('d')).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(6).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(1).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(0).value,
    ctypes.c_uint8(0).value
]

# track header
trackhdr = [
    ctypes.c_uint8(ord('M')).value,
    ctypes.c_uint8(ord('T')).value,
    ctypes.c_uint8(ord('r')).value,
    ctypes.c_uint8(ord('k')).value
]


class TrackInfo:

    def __init__(self):
        self._velocity = None
        self._deltaT = None
        self._lastEvent = None

    @property
    def velocity(self):
        return self._velocity.value

    @velocity.setter
    def velocity(self, value):
        self._velocity = ctypes.c_char(value)

    @property
    def deltaT(self):
        return self._deltaT.value

    @deltaT.setter
    def deltaT(self, value):
        self._deltaT = ctypes.c_long(value)

    @property
    def lastEvent(self):
        return self._lastEvent.value

    @lastEvent.setter
    def lastEvent(self, value):
        self._lastEvent = ctypes.c_uint8(value)


class Midi:
    divisions = 0
    
    tracks = list(map(lambda i: [], range(MIDI_TRACKS)))

    @property
    def trackCount(self):
        return len(list(filter(lambda i: len(i) > 0, self.tracks)))


class MusEvent:

    RELEASE_NOTE = 0
    PLAY_NOTE = 1
    BEND_NOTE = 2
    SYSTEM = 3
    CONTROLLER = 4
    UNKNOWN_EVENT_1 = 5
    SCORE_END = 6
    UNKNOWN_EVENT_2 = 7


class MusControllers:

    INSTRUMENT = 0
    BANK = 0x00
    MODULATION = 0x01
    VOLUME = 0x07
    PAN = 0x0A
    EXPRESSION = 0x0B
    REVERB = 0x5B
    CHOROUS = 0x5D
    SUSTAIN_PEDAL = 0x40
    SOFT_PEDAL = 0x43
    SOUNDS_OFF = 0x78
    NOTES_OFF = 0x7B
    MONO = 0x7E
    POLY = 0x7F
    RESET_ALL = 0x79

    
ctrlMus2Midi = [
    0,    # Not used.
    0x00, # Bank select.
    0x01, # Modulation.
    0x07, # Volume.
    0x0A, # Pan.
    0x0B, # Expression.
    0x5B, # Reverb.
    0x5D, # Chorus.
    0x40, # Sustain pedal.
    0x43, # Soft pedal.
    
    # The valueless controllers:
    0x78, # All sounds off.
    0x7B, # All notes off.
    0x7E, # Mono.
    0x7F, # Poly.
    0x79  # Reset all controllers.
]


M32 = 0xffffffff
M16 = 0xffff
M8 = 0xff

def m32(n):
    return n & M32

def m16(n):
    return n & M16

def m8(n):
    return n & M8

def madd(T, a, b):
    return T(a+b)

def msub(T, a, b):
    return T(a-b)

def mls(T, a, b):
    return T(a<<b)

def mrs(T, a, b):
    return T(a >> b)

def mand(T, a, b):
    return T(a & b)

def mnot(T, a):
    return T(~a)


def last(e):
    return mand(m8, e, 0x80)


def event_type(e):
    x = mand(m8, e, 0x80)
    return mrs(m8, x, 4)


def channel(e):
    return mand(m8, e, 0x0F)


class MusDecoder:

    @staticmethod
    def decode_mus_to_midi(lump):
        mididata = MusDecoder.decode_mus_to_mid(lump)      
        return MusDecoder.decode_mid_to_midi(mididata)


    @staticmethod
    def decode_mid_to_midi(mididata):
        total = len(midihdr)
        numTracks = 0

        for i in range(MIDI_TRACKS):
            have_track = mididata.tracks[i] is not None

            if have_track:
                total += 8 + len(mididata.tracks[i])
                numTracks += 1

        mid = [] + midihdr
        mid[10] = 0
        mid[11] = numTracks   # set number of tracks in header
        mid[12] = ctypes.c_uint8((mididata.divisions >> 8) & 0x7f).value
        mid[13] = ctypes.c_uint8((mididata.divisions) & 0xff).value

        # write the tracks
        for i in range(MIDI_TRACKS):
            have_track = mididata.tracks[i] is not None

            if have_track:
                # copy track header
                mid += trackhdr

                # write track length
                mid += MusDecoder.writeLength( len(mididata.tracks[i]))

                # copy track data
                mid += mididata.tracks[i]
                
        midBuffer = b''
        for i in mid:
            midBuffer += struct.pack(">B", i)
        
        return midBuffer
                
    
    @staticmethod
    def writeByte(mididata, tracknum, value):
        mididata.tracks[tracknum].append(
            ctypes.c_uint8(value).value
        )

    
    @staticmethod
    def writeVarLen(mididata, tracknum, value):
        long_value = ctypes.c_ulong(value).value
        buf = None

        buf = ctypes.c_ulong(value & 0x7F).value
        while True:
            long_value = ctypes.c_ulong(value >> 7).value
            finished = ctypes.c_ulong(~value).value
            if finished > 0:
                break

            buf = ctypes.c_ulong(buf << 8).value
            buf = ctypes.c_ulong(buf | 0x80).value
            buf = ctypes.c_ulong(buf + (long_value & 0x7F)).value

        while True:
            val = ctypes.c_uint8(buf & 0xff).value
            MusDecoder.writeByte(mididata, tracknum, val)

            if ctypes.c_ulong(buf & 0x80).value:
                buf = ctypes.c_ulong(buf >> 8)
            else:
                break

    @staticmethod
    def writeLength(value):
        return [
            ctypes.c_uint8((value >> 24) & 0xFF).value,
            ctypes.c_uint8((value >> 16) & 0xFF).value,
            ctypes.c_uint8((value >> 8) & 0xFF).value,
            ctypes.c_uint8(value & 0xFF).value
        ]


    @staticmethod
    def midiEvent(mididata, midicode, midiChannel, midiTrack, trackInfo, noComp):
        newEvent = ctypes.c_uint8(midicode | midiChannel).value
        isLastEvent = newEvent == trackInfo[midiTrack].lastEvent

        if not isLastEvent or noComp:
            MusDecoder.writeByte(mididata, midiTrack, newEvent)
            trackInfo[midiTrack].lastEvent = newEvent

        return newEvent
    

    @staticmethod
    def decode_mus_to_mid(lump, division=89, nocomp=True):
        header = MusDecoder.parse_header(lump)
        buf = io.BytesIO(lump.data)

        # int
        MUS2MIDchannel = list(map(lambda x: -1, range(MIDI_TRACKS)))
        # ubyte
        MIDIchan2track = list(map(lambda x: 0, range(MIDI_TRACKS)))

        score_length = header['score_length']
        score_start = header['score_start']
        number_channels = header['channels']

        # boon engine has this as score_length + score_start but that doesnt make sense
        muslen = score_length - score_start
        mus_empty = muslen <= 0
        if mus_empty:
            raise Exception('mus data empty')

        too_many_channels = number_channels > 15
        if too_many_channels:
            raise Exception('too many channels [{0}]'.format(number_channels))
        
        tracks = list(map(lambda i: TrackInfo(), range(MIDI_TRACKS)))        
        for track in tracks:
            track.velocity = 64
            track.deltaT = 0
            track.lastEvent = 0

        d = division
        if ~d:
            d = 70

        mididata = Midi()
        mididata.divisions = d
        mididata.tracks[0] = midikey + miditempo
        
        buf.seek(score_start) # got to start of score

        MIDIchannel = None
        MIDItrack = None

        while buf.tell() < muslen:

            e = struct.unpack("<B", buf.read(1))[0]
            event = event_type(e)
            musChannel = channel(e)

            print ("event:", event, e)
            
            if event == MusEvent.SCORE_END:
                print("score_end!")
                break

            channel_not_initilized = MUS2MIDchannel[musChannel] == -1
            if channel_not_initilized:
                # set midi channel to miditrack
                if musChannel == 15:
                    MUS2MIDchannel[musChannel] = 9
                    
                else:
                    maxChannel = max(MUS2MIDchannel)
                    firstAvailable = 10 if maxChannel == 8 else maxChannel + 1
                    MUS2MIDchannel[musChannel] = firstAvailable
                    
                MIDIchannel = MUS2MIDchannel[musChannel]
                MIDItrack = MIDIchan2track[MIDIchannel] = mididata.trackCount + 1
            
            else:
                MIDIchannel = MUS2MIDchannel[musChannel]
                MIDItrack = MIDIchan2track[MIDIchannel]

            MusDecoder.writeVarLen(mididata, MIDItrack, tracks[MIDItrack].deltaT)
            tracks[MIDItrack].deltaT = 0

            if event == MusEvent.RELEASE_NOTE:
                newEvent = MusDecoder.midiEvent(mididata,
                                                0x90,
                                                MIDIchannel,
                                                MIDItrack,
                                                tracks,
                                                True)

                data = struct.unpack("<B", buf.read(1))[0]
                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     ctypes.c_uint8(data & 0x7F).value)
                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     0)

            elif event == MusEvent.PLAY_NOTE:
                newEvent = MusDecoder.midiEvent(mididata,
                                                0x90,
                                                MIDIchannel,
                                                MIDItrack,
                                                tracks,
                                                nocomp)
                data = struct.unpack("<B", buf.read(1))[0]
                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     ctypes.c_uint8(data & 0x7F).value)
                
                check = ctypes.c_uint8(data & 0x80).value
                if check:
                    data = struct.unpack("<B", buf.read(1))[0]
                    tracks[MIDItrack].velocity = ctypes.c_uint8(data & 0x7F).value

                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     tracks[MIDItrack].velocity)

            elif event == MusEvent.BEND_NOTE:
                newEvent = MusDecoder.midiEvent(mididata,
                                                0xE0,
                                                MIDIchannel,
                                                MIDItrack,
                                                tracks,
                                                nocomp)
                data = struct.unpack("<B", buf.read(1))[0]
                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     ctypes.c_uint8((data & 1) << 6).value)
                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     ctypes.c_uint8(data >> 1).value)

            elif event == MusEvent.SYSTEM:
                newEvent = MusDecoder.midiEvent(mididata,
                                                0xB0,
                                                MIDIchannel,
                                                MIDItrack,
                                                tracks,
                                                nocomp)
                data = struct.unpack("<B", buf.read(1))[0]
                if (data < 10) or (data > 14):
                    raise Exception("bad system event [{0}]".format(data))

                MusDecoder.writeByte(mididata,
                                     MIDItrack,
                                     ctrlMus2Midi[data])
                if data == 12:
                    val = ctypes.c_uint8(number_channels + 1).value
                    MusDecoder.writeByte(mididata, MIDItrack, val)
                else:
                    MusDecoder.writeByte(mididata, MIDItrack, 0)

            elif event == MusEvent.CONTROLLER:
                data = struct.unpack("<B", buf.read(1))[0]
                if data > 9:
                    raise Exception("bad controller value [{0}]".format(data))

                if data:
                    newEvent = MusDecoder.midiEvent(mididata,
                                                    0xB0,
                                                    MIDIchannel,
                                                    MIDItrack,
                                                    tracks,
                                                    nocomp)
                    MusDecoder.writeByte(mididata,
                                         MIDItrack,
                                         ctrlMus2Midi[data])
                else:
                    newEvent = MusDecoder.midiEvent(mididata,
                                                    0xC0,
                                                    MIDIchannel,
                                                    MIDItrack,
                                                    tracks,
                                                    nocomp)
                    data = struct.unpack("<B", buf.read(1))[0]
                    val = ctypes.c_uint8(data & 0x7F).value
                    MusDecoder.writeByte(mididata, MIDItrack, val)

            elif (event == MusEvent.UNKNOWN_EVENT_1) \
                 or (event == MusEvent.UNKNOWN_EVENT_2):
                raise Exception("bad event - unknown 1 or 2")

            else:
                raise Exception("bad event - really-unknown [{0}]".format(event))

        if event != MusEvent.SCORE_END:
            raise Exception('something wrong did not reach score-end')

        for i in range(MIDI_TRACKS):
            have_track = mididata.tracks[i] is not None

            if have_track:
                MusDecoder.writeByte(mididata, i, 0x00)
                MusDecoder.writeByte(mididata, i, 0xFF)
                MusDecoder.writeByte(mididata, i, 0x2F)
                MusDecoder.writeByte(mididata, i, 0x00)
             
        return mididata
            

    @staticmethod
    def parse_header(lump):
        data = io.BytesIO(lump.data)
        identifier = struct.unpack("<4s", data.read(4))[0]
        score_length, \
            score_start, \
            channels, \
            sec_channels, \
            instrument_count, \
            padding = struct.unpack("<HHHHHH", data.read(12))

        if b"MUS" not in identifier:
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
