from PyDoom.Definitions import Vertex
from PyDoom.MathUtils import rad
from PyDoom.Constants import *

import math


class Player:

    _position = Vertex(0, 0)
    _angle = 0.0  # 0 is north, clockwise, degrees

    @property
    def position(self):
        return self._position

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    def move_player_pos(self, mult, rotation_degrees):
        self.position.x = self.position.x + math.sin(rad(self.angle + rotation_degrees)) * SPEED * mult
        self.position.y = self.position.y + math.cos(rad(self.angle + rotation_degrees)) * SPEED * mult
