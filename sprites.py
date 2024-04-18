# Sprite files that contain all sprites required for simulation

import viz
import vizshape
from constants import *
from mathematicalMethods import *
import math
import copy

class Point:
    def __init__(self, pos, colour, radius, initialVelocity, initialForce):
        self.object = vizshape.addSphere()
        self.colour = colour
        self.radius = radius
        
        self.pos = pos
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.oldPos[axis] -= initialVelocity[axis]
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        self.mass = SIMULATED_PROTON_MASS
        self.momentum = [0, 0, 0]
        self.force = initialForce
        self.volume = 4/3 * math.pi * ((self.radius) ** 3)
        self.density = self.mass / self.volume
        
    def enablePhysics(self):
        '''Method that enables the point's physics'''
        self.enableNewtonianMechanics()

    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        # Basic Newtonian Mechanics (Kinematics, Dynamics, Verlet Integration)
        # 1. Obtain acceleration by F = ma
        # 2. Obtain velocity by difference in pos and old pos over time
        # 3. Update pos based on s = vt
        # 4. Don't change position directly, change velocity so use oldPos (which is a record of the position of the proton before the frame) -- Analogy: A slingshot; the further you pull the ball back, the higher the velocity of projection
        for axis in range(3):
            self.acceleration[axis] = self.force[axis] / self.mass
            self.oldPos[axis] -= self.acceleration[axis] / (RATE_OF_CALCULATIONS ** 2)
            self.velocity[axis] = (self.pos[axis] - self.oldPos[axis]) * RATE_OF_CALCULATIONS # Rate of calculations used to reduce floating point errors
            self.momentum[axis] = self.mass * self.velocity[axis]
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.pos[axis] += self.velocity[axis] / RATE_OF_CALCULATIONS

        
    def draw(self):
        '''Method that draws the point'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.setScale((self.radius, self.radius, self.radius)) # Allows changing of sphere orientation
        
class Cuboid:
    def __init__(self, pos, colour, size):
        self.pos = pos
        self.colour = colour
        self.size = size
        self.object = vizshape.addBox(size = size)
        
    def draw(self, alpha):
        self.object.setPosition(self.pos)
        self.object.color(self.colour)
        self.object.alpha(alpha)
        
class Cylinder:
    def __init__(self, pos, colour, radius, height, axis):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.height = height
        self.axis = axis
    
    def draw(self, alpha):
        '''Method that draws the cylinders'''
        self.object = vizshape.addCylinder(height = self.height, radius = self.radius, axis = self.axis)
        self.object.setPosition(self.pos)
        self.object.color(self.colour)
        self.object.alpha(alpha)
        
class Frustrum(Cylinder):
    def __init__(self, pos, colour, radius, height, axis, bottomRadius):
        super().__init__(pos, colour, radius, height, axis)
        self.bottomRadius = bottomRadius
        
    def draw(self, alpha):
        '''Method that draws the frustrum'''
        self.object = vizshape.addCylinder(height = self.height, radius = self.radius, axis = self.axis, bottomRadius = self.bottomRadius)
        self.object.setPosition(self.pos)
        self.object.color(self.colour)
        self.object.alpha(alpha)

class HydrogenAtom(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, RED, radius, initialVelocity, initialForce)

    def enablePhysics(self):
        '''Method that enables the hydrogen atom's physics'''
        super().enablePhysics()

    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        super().enableNewtonianMechanics()

    def draw(self):
        '''Method that draws the hydrogen atom'''
        super().draw()

class Proton(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, PURPLE, radius, initialVelocity, initialForce)
        self.orbitalCentre = ORIGIN
        self.orbitalRadius = getMagnitude(self.orbitalCentre, self.pos)
        self.charge = SIMULATED_PROTON_CHARGE
        self.magneticForce = [0, 0, 0]
        self.electrostaticForce = [0, 0, 0]

    def enablePhysics(self):
        '''Method that enables the hydrogen atom's physics'''
        super().enablePhysics()

    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        for axis in range(3):
            self.force[axis] = self.magneticForce[axis] + self.electrostaticForce[axis]
            self.acceleration[axis] = self.force[axis] / self.mass
            self.oldPos[axis] -= self.acceleration[axis] / (RATE_OF_CALCULATIONS ** 2)
            self.velocity[axis] = (self.pos[axis] - self.oldPos[axis]) * RATE_OF_CALCULATIONS # Rate of calculations used to reduce floating point errors
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.pos[axis] += self.velocity[axis] / RATE_OF_CALCULATIONS

    def enableUniformCircularMotion(self):
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

    def getElectrostaticForce(self):
        '''Method that obtains the electrostatic force which causes the acceleration of the protons'''
        for axis in range(3):
            self.electrostaticForce[axis] = 3

    def draw(self):
        '''Method that draws the hydrogen atom'''
        super().draw()
        
class Tube(Cylinder):
    def __init__(self, pos, colour, radius, height, axis):
        super().__init__(pos, colour, radius, height, axis)
        
    def draw(self, alpha):
        '''Method that draws the tubes'''
        super().draw(alpha)

class SourceChamber(Cylinder):
    def __init__(self, pos, colour, radius, height, axis):
        super().__init__(pos, colour, radius, height, axis)
        self.wall = Frustrum([0, 5, -9], GREEN, 3, 5, vizshape.AXIS_Z, 0.5)
        # Radius 2
        self.positivePlate = ChargedPlate([0, 9.5, -4], PURPLE, (3, 3, 5), "+")
        self.negativePlate = ChargedPlate([0, 0.5, -4], PURPLE, (3, 3, 5), "-")
            
    def draw(self, alpha):
        '''Method that draws the source chamber'''
        super().draw(alpha)
        self.wall.draw(0.5)
        self.positivePlate.draw(0.5)
        self.negativePlate.draw(0.5)
        
class ChargedPlate(Cuboid):
    def __init__(self, pos, colour, size, charge):
        super().__init__(pos, colour, size)
        self.charge = charge
        
    def draw(self, alpha):
        '''Method that draws the charged plate'''
        super().draw(alpha)

class Collider:
    def __init__(self, pos, colour, radius, tubeRadius):
        self.pos = pos # Centre
        self.colour = colour
        self.radius = radius
        self.tubeRadius = tubeRadius
        self.object = vizshape.addTorus(radius = self.radius, tubeRadius = self.tubeRadius)

    def draw(self, alpha):
        '''Method that draws the collider'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.alpha(alpha)

        
    