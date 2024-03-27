# Sprite files that contain all sprites required for simulation

import viz
import vizshape
from constants import *
from mathematicalMethods import *
import math
import copy

class Proton:
    def __init__(self, pos, colour, radius, simulation):
        self.object = vizshape.addSphere()
        self.colour = colour
        self.radius = radius
        self.simulation = simulation
        
        self.pos = pos
        self.orbitalCentre = ORIGIN
        self.orbitalRadius = getMagnitude(self.orbitalCentre, self.pos)
        self.oldPos = [pos[0] - 0.01, pos[1], pos[2]]
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        self.mass = PROTON_MASS
        self.force = [0, 0, 0]
        self.volume = 4/3 * math.pi * ((self.radius) ** 3)
        self.density = self.mass / self.volume
        self.magneticForce = [0, 0, 0]
        self.electrostaticForce = [0, 0, 0]
        self.startTime = 0

        self.simulation = simulation
        self.collider = self.simulation.collider
        
    def move(self):
        '''Move the proton'''
        # Basic Newtonian Mechanics (Kinematics, Dynamics, Verlet Integration)
        # 1. Obtain acceleration by F = ma
        # 2. Obtain velocity by difference in pos and old pos over time
        # 3. Update pos based on s = vt
        # 4. Don't change position directly, change velocity so use oldPos (which is a record of the position of the proton before the frame) -- Analogy: A slingshot; the further you pull the ball back, the higher the velocity of projection
        self.nonUniformCircularMotion()
        for axis in range(3):
            self.force[axis] = self.magneticForce[axis] + self.electrostaticForce[axis]
            self.acceleration[axis] = self.force[axis] / self.mass
            self.oldPos[axis] -= self.acceleration[axis] / (RATE_OF_CALCULATIONS ** 2)
            self.velocity[axis] = (self.pos[axis] - self.oldPos[axis]) * RATE_OF_CALCULATIONS # Rate of calculations used to reduce floating point errors
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.pos[axis] += self.velocity[axis] / RATE_OF_CALCULATIONS

    def uniformCircularMotion(self):
        '''Method that manages uniform circular motion'''
        # Uniform Circular Motion
        # 1. Get direction and angle
        # 2. Get orbital radius and speed
        # 3. Apply F = mv^2 / r
        resultantDirection = getQuartiles(self.orbitalCentre, self.pos)
        angle = getTwoDAngle(self.orbitalCentre, self.pos)
        self.speed = getMagnitude(self.orbitalCentre, self.velocity)
        resultantForce = self.mass * (self.speed ** 2) / self.orbitalRadius
        self.magneticForce = [-resultantDirection[0] * resultantForce * math.cos(angle), 0, -resultantDirection[1] * resultantForce * math.sin(angle)] # Negative resultant direction required

    def nonUniformCircularMotion(self):
        '''Method that manages non-uniform circular motion'''
        # Non-uniform circular motion
        # 1. Get direction and angle of motion of linear velocity
        # 2. Get magnetic force using the uniform circular function
        # 3. Sum the electrostaticforce with the resultant force
        directionOfMotion = getQuartiles(self.orbitalCentre, self.velocity)
        angleOfMotion = getTwoDAngle(self.orbitalCentre, self.velocity)
        self.uniformCircularMotion()
        resultantForce = 0.1
        self.electrostaticForce = [directionOfMotion[0] * resultantForce * math.cos(angleOfMotion), 0, directionOfMotion[1] * resultantForce * math.sin(angleOfMotion)]
        print(self.electrostaticForce)
        

    def draw(self):
        '''Draw the proton'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.setScale((self.radius, self.radius, self.radius)) # Allows changing of sphere orientation

class Collider:
    def __init__(self, pos):
        self.object = vizshape.addTorus(radius = 20, tubeRadius = 3)
        self.pos = pos # Centre
        
    