# Sprite files that contain all sprites required for simulation

import viz
import vizshape
from constants import *
import math
import copy

class Proton:
    def __init__(self, pos, colour, radius):
        self.object = vizshape.addSphere()
        self.colour = colour
        self.radius = radius
        
        self.pos = pos
        self.oldPos = pos
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        self.mass = PROTON_MASS
        self.force = [1, 0, 0]
        self.volume = 4/3 * math.pi * ((self.radius) ** 3)
        self.density = self.mass / self.volume
        
    def move(self):
        '''Move the proton'''
        # Basic Newtonian Mechanics (Kinematics, Dynamics, Verlet Integration)
        # 1. Obtain acceleration by F = ma
        # 2. Obtain velocity by difference in pos and old pos over time
        # 3. Update pos based on s = vt
        # 4. Don't change position directly, change velocity so use oldPos (which is a record of the position of the proton before the frame) -- Analogy: A slingshot; the further you pull the ball back, the higher the velocity of projection
        for axis in range(3):
            self.acceleration[axis] = self.force[axis] / self.mass
            self.oldPos[axis] -= self.acceleration[axis] / (RATE_OF_CALCULATIONS ** 2)
            self.velocity[axis] = (self.pos[axis] - self.oldPos[axis]) * RATE_OF_CALCULATIONS # Rate of calculations used to reduce floating point error
        print(self.velocity)
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.pos[axis] += self.velocity[axis] / RATE_OF_CALCULATIONS


    def draw(self):
        '''Draw the proton'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.setScale((self.radius, self.radius, self.radius)) # Allows changing of sphere orientation
