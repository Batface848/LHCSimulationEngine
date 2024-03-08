# Sprite files that contain all sprites required for simulation

import viz
import vizshape
from constants import *
from math import *

class Proton:
    def __init__(self, pos, colour, radius):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.mass = PROTON_MASS * RADIUS_SCALE_FACTOR
        self.volume = 4/3 * pi * 3 * ((self.radius) ** 3)
        self.density = self.mass / self.volume

    def draw(self):
        '''Draw the proton'''
        self.object = vizshape.addSphere()
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
