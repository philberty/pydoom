from PyDoom.WadException import WadException
from PyDoom.WadDirectory import WadDirectory
from PyDoom.WadPalette import WadPlaypal
from PyDoom.WadLevel import WadLevel
from PyDoom import LOG as logger

from typing import Dict

import struct
import os
import re


WAD_HEADER_SIZE = 12
WAD_DIRECTORY_SIZE = 16


class WadFile(dict):

## Fields

    _wad_file = None
    _wad_type = None
    _wad_levels = {}
    _number_of_lumps = 0
    _info_table_offset = 0
    _playpals = None
    
## Constructor

    def __init__(self):
        # init super dict
        super(WadFile, self).__init__()

    @staticmethod
    def load(wadfile):
        # ensures file exists
        with open(wadfile, "rb"):
            instance = WadFile()
            instance._wad_file = os.path.abspath(wadfile)
            instance._verify()
            instance._load_directories()
            return instance

## Properties

    @property
    def log(self):
        return logger

    @property
    def wad_file_path(self):
        return self._wad_file

    @property
    def wad_file_type(self):
        return self._wad_type

    @property
    def number_of_lumps(self):
        return self._number_of_lumps

    @property
    def info_table_offset(self):
        return self._info_table_offset

    @property
    def wad_levels(self) -> Dict[str, WadLevel]:
        return self._wad_levels

    @property
    def playpals(self):
        return self._playpals

## Methods

    def get_lumps_by_prefix(self, prefix):
        possible_keys = filter(lambda i: i.startswith(prefix), self.keys())
        return tuple(map(lambda i: self[i][0], possible_keys))

    def _verify(self):
        """
        Verify this is a valid WAD
        """
        with open(self.wad_file_path, "rb") as fd:
            self._wad_type = fd.read(4).decode("utf-8")
            self._number_of_lumps = struct.unpack("<I", fd.read(4))[0]
            self._info_table_offset = struct.unpack("<I", fd.read(4))[0]

            wad_types = ("IWAD", "PWAD")
            if self.wad_file_type not in wad_types:
                raise WadException("Found invalid wad file [%s]" % self.wad_file_type)

    def _load_directories(self):
        """
        Load the directory table
        """
        with open(self.wad_file_path, "rb") as fd:
            # parser state
            is_level = False
            current_level = None
            current_level_lumps = None

            # read in directories
            for i in range(self.number_of_lumps):
                # next lump
                fd.seek(self.info_table_offset + (i * WAD_DIRECTORY_SIZE))
                current_lump = fd.read(WAD_DIRECTORY_SIZE)

                # read in directory data
                offset = struct.unpack("<I", current_lump[0:4])[0]
                size = struct.unpack("<I", current_lump[4:8])[0]
                name = current_lump[8:16].decode('utf-8').rstrip('\0')

                self.log.debug("found lump [{0}]".format(name))

                # load lump data
                data = None
                if offset > 0:
                    fd.seek(offset)
                    data = fd.read(size)

                # we now have a full directory element
                directory = WadDirectory(name, offset, size, data)

                if name == "PLAYPAL":
                    self._playpals = WadPlaypal(directory)

                # Level parser
                if re.match('E\dM\d|MAP\d\d', name):
                    self.log.info("New Level found: {0}".format(name))
                    is_level = True
                    current_level = name
                    current_level_lumps = {}

                if is_level:
                    # add the directory to the level
                    current_level_lumps[name] = directory

                    # Each level is delimited by its own blockmap lump
                    if name == "BLOCKMAP":
                        is_level = False
                        level = WadLevel(current_level,
                                         current_level_lumps["THINGS"],
                                         current_level_lumps["LINEDEFS"],
                                         current_level_lumps["SIDEDEFS"],
                                         current_level_lumps["VERTEXES"],
                                         current_level_lumps["SEGS"],
                                         current_level_lumps["SSECTORS"],
                                         current_level_lumps["NODES"],
                                         current_level_lumps["SECTORS"],
                                         current_level_lumps["REJECT"],
                                         current_level_lumps["BLOCKMAP"],
                                         self)
                        self._wad_levels[current_level] = level

                # add into directory list
                try:
                    container = self[name]
                    container.append(directory)
                except KeyError:
                    container = [directory]
                finally:
                    self[name] = container
