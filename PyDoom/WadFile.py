from PyDoom.WadException import WadException
from PyDoom.WadDirectory import WadDirectory
from PyDoom.WadLevel import WadLevel

import logging
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

## Constructor

    def __init__(self, wadfile):
        # init super dict
        super(WadFile, self).__init__()

        # ensures file exists
        with open(wadfile, "rb"):
            self._wad_file = os.path.abspath(wadfile)
            self._verify()
            self._load_directories()

## Properties

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
    def wad_levels(self):
        return self._wad_levels

## Emulation

    def __repr__(self):
        return "WadFile Object"

    def __str__(self):
        return "Wad File: %s of type [%s] [nLumps %i]" \
               % (self.wad_file_path, self.wad_file_type, self.number_of_lumps)

## Methods

    """
    Verify this is a valid WAD
    """
    def _verify(self):
        with open(self.wad_file_path, "rb") as fd:
            self._wad_type = fd.read(4).decode("utf-8")
            self._number_of_lumps = struct.unpack("<I", fd.read(4))[0]
            self._info_table_offset = struct.unpack("<I", fd.read(4))[0]
            if self.wad_file_type != "IWAD":
                raise WadException("Found invalid wad file [%s]" % self.wad_file_type)

    """
    Load the directory table
    """
    def _load_directories(self):
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

                # load lump data
                data = None
                if offset > 0:
                    fd.seek(offset)
                    data = fd.read(size)

                # we now have a full directory element
                directory = WadDirectory(name, offset, size, data)

                # Level parser
                if re.match('E\dM\d|MAP\d\d', name):
                    logging.debug("New Level: " + name)
                    is_level = True
                    current_level = name
                    current_level_lumps = {}

                if is_level:
                    logging.debug("Adding lump [%s] to Level [%s]" % (name, current_level))
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
                                         current_level_lumps["BLOCKMAP"])
                        self._wad_levels[current_level] = level

                # add into directory list
                try:
                    container = self[name]
                    container.append(directory)
                except KeyError:
                    container = [directory]
                    logging.debug("New Directory: " + name)
                finally:
                    self[name] = container
