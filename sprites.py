# Sprite files that contain all sprites required for simulation

import viz
import vizshape
from constants import *
from mathematicalMethods import *
import math
import copy

# Points

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
        self.electroMagneticForce = [0, 0, 0]
        
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


class HydrogenAtom(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, RED, radius, initialVelocity, initialForce)
        self.electroMagneticForce = [0, 0, 0]
        self.startedCircularMotion = False
        self.velocity = initialVelocity

    def enablePhysics(self):
        '''Method that enables the hydrogen atom's physics'''
        self.enableNewtonianMechanics()

    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        for axis in range(3):
            self.acceleration[axis] = self.force[axis] / self.mass
            self.oldPos[axis] -= self.acceleration[axis] / (RATE_OF_CALCULATIONS ** 2)
            self.velocity[axis] = (self.pos[axis] - self.oldPos[axis]) * RATE_OF_CALCULATIONS # Rate of calculations used to reduce floating point errors
            self.momentum[axis] = self.mass * self.velocity[axis]
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.pos[axis] += self.velocity[axis] / RATE_OF_CALCULATIONS
        
    def circularMotion(self, centre, radius):
        '''Method that manages circular motion in the booster ring and the actual collider'''
        # 1. Get direction and angle
        # 2. Get orbital radius and speed
        # 3. Apply F = mv^2/r
        print("Applying Circular Motion")
        self.orbitalCentre = centre
        self.orbitalRadius = radius
    
        # Debugging statements
        print(f"Centre: {centre}, Radius: {radius}")
    
        resultantDirection = getQuartiles(self.orbitalCentre, self.pos)
        angle = getTwoDAngle(self.orbitalCentre, self.pos)
        self.speed = getMagnitude(self.orbitalCentre, self.velocity)
    
        # More debugging statements
        print(f"Resultant Direction: {resultantDirection}")
        print(f"Angle: {angle}")
        print(f"Speed: {self.speed}")
    
        resultantForce = self.mass * (self.speed ** 2) / self.orbitalRadius
    
        # Even more debugging statements
        print(f"Resultant Force: {resultantForce}")
    
        self.force = [
        -resultantDirection[0] * resultantForce * math.cos(angle), 
        0, 
        -resultantDirection[2] * resultantForce * math.sin(angle)
    ]
    
        # Final debugging statement
        print(f"Force: {self.force}")
        
    def numericalCircularMotion(self, centre, radius, initialVelocity = None):
        '''Method that manages circular motion in the booster ring and the actual collider using a numerical method'''
        # 1. Calculate angular velocity from the starting velocity and the orbital radius
        # 2. Calculate the new angle based on the angular velocity and adjust the point's position
        print("Applying Numerical Circular Motion")
        self.orbitalCentre = centre
        self.orbitalRadius = radius
        if initialVelocity is not None:
            self.speed = getMagnitude(ORIGIN, initialVelocity)
            self.angularVelocity = self.speed / self.orbitalRadius
            self.changeInAngle = -self.angularVelocity / RATE_OF_CALCULATIONS
            
        currentAngle = getTwoDAngle(self.orbitalCentre, self.pos)
        newAngle = currentAngle + self.changeInAngle
        if newAngle > (2 * math.pi):
            newAngle = newAngle - (math.pi * 2)
        print(f"Pos: {self.pos}")
        print(f"Current Angle: {currentAngle}")
        print(f"New Angle: {newAngle}")
        newPos = [self.orbitalCentre[0] + self.orbitalRadius * math.cos(newAngle), self.orbitalCentre[1], self.orbitalCentre[2] + self.orbitalRadius * math.sin(newAngle)]
        self.pos = newPos
        
    def draw(self):
        '''Method that draws the hydrogen atom'''
        super().draw()


class Proton(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce, boosterRing, collider):
        super().__init__(pos, PURPLE, radius, initialVelocity, initialForce)
        self.initialForce = initialForce
        self.charge = SIMULATED_PROTON_CHARGE
        self.boosterRing = boosterRing
        self.speed = 0
        self.completedLINAC = False
        self.collider = collider
        self.electroMagneticForce = [0, 0, 0]
        self.boosting = False
        self.deflectionDirection = None
        self.passingThroughTube = False
        self.completedTube = False
        self.goingThroughCollider = False
        self.collided = False

    def enablePhysics(self):
        '''Method that enables the hydrogen atom's physics'''
        if self.collided:
            self.velocity = [0, 0, 0]
            self.speed = 0
        else:
            if self.completedTube:
                if self.pos[1] < 12:
                    targetAnglePlus = math.asin(self.pos[2] / 138)
                    targetAngleMinus = math.asin(self.pos[2] / 142)
                    self.xDistancePlus = (138 * math.cos(targetAnglePlus))
                    self.xDistanceMinus = (142 * math.cos(targetAngleMinus))
                    print(self.xDistanceMinus)
                    self.differencePlus = self.xDistancePlus - 79
                    self.differenceMinus = self.xDistanceMinus - 129
                    self.adjustAxesForCollider(self.pos)
                else:
                    if not self.goingThroughCollider:
                        if self.deflectionDirection == "+":
                            self.numericalCircularMotion(self.collider.pos, 138, "c", [0, 0, -4000])
                        else:
                            self.numericalCircularMotion(self.collider.pos, 142, "a", [0, 0, 4000])
                        self.goingThroughCollider = True
                    else:
                        if self.deflectionDirection == "+":
                            self.numericalCircularMotion(self.collider.pos, 138, "c")
                        else:
                            self.numericalCircularMotion(self.collider.pos, 142, "a")
                    
            else:
                if self.collider.started:
                    if not self.passingThroughTube:
                        if self.boosting and self.speed >= 4000:
                            self.force = [0, 0, 0]
                            if self.deflectionDirection == "-":
                                self.pos = [-31, 8, -131]
                                velocity = [-(self.speed // 200), 0, 0]
                                self.force = [-0.00000001, 0, 0]
                            else:
                                self.pos = [-31, 8, -69] 
                                velocity = [(self.speed // 200), 0, 0]
                                self.force = [0.00000001, 0, 0]
                            self.oldPos = copy.deepcopy(self.pos)
                            for axis in range(3):
                                self.oldPos[axis] -= velocity[axis]
                            self.passingThroughTube = True
                        else:
                            self.numericalCircularMotion(self.boosterRing.pos, 31, "c")
                    else:
                        self.enableNewtonianMechanics()
                        if self.deflectionDirection == "-" and self.pos[0] < -129:
                            self.pos = [-129, 8, -131]
                            self.completedTube = True
                        if self.deflectionDirection == "+" and self.pos[0] > 79:
                            self.pos = [79, 8, -69] 
                            self.completedTube = True
                    
                else:
                    if self.completedLINAC:
                        if self.pos[0] > -0.004 and self.pos[1] < 6.5:
                            self.adjustAxesForBoosterRing(self.pos)
                        else:
                            if not self.boosting:
                                self.numericalCircularMotion(self.boosterRing.pos, 31, "c", self.velocity)
                                self.boosting = True
                            else:
                                self.numericalCircularMotion(self.boosterRing.pos, 31, "c")
                    else:
                        self.enableNewtonianMechanics()

    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        for axis in range(3):
            self.acceleration[axis] = self.force[axis] / self.mass
            self.oldPos[axis] -= self.acceleration[axis] / (RATE_OF_CALCULATIONS ** 2)
            self.velocity[axis] = (self.pos[axis] - self.oldPos[axis]) * RATE_OF_CALCULATIONS # Rate of calculations used to reduce floating point errors
            self.momentum[axis] = self.mass * self.velocity[axis]
        self.oldPos = copy.deepcopy(self.pos)
        for axis in range(3):
            self.pos[axis] += self.velocity[axis] / RATE_OF_CALCULATIONS
        
    def circularMotion(self, centre, radius):
        '''Method that manages circular motion in the booster ring and the actual collider'''
        # 1. Get direction and angle
        # 2. Get orbital radius and speed
        # 3. Apply F = mv^2/r
        print("Applying Circular Motion")
        self.orbitalCentre = centre
        self.orbitalRadius = radius
        resultantDirection = getQuartiles(self.orbitalCentre, self.pos)
        angle = getTwoDAngle(self.orbitalCentre, self.pos)
        self.orbitalRadius = radius
        self.speed = getMagnitude(self.orbitalCentre, self.velocity)
        resultantForce = self.mass * (self.speed ** 2) / self.orbitalRadius
        self.force = [-resultantDirection[0] * resultantForce * math.cos(angle), 0, -resultantDirection[2] * resultantForce, math.sin(angle)]
        
    def numericalCircularMotion(self, centre, radius, direction, initialVelocity = None):
        '''Method that manages circular motion in the booster ring and the actual collider using a numerical method'''
        # 1. Calculate angular velocity from the starting velocity and the orbital radius
        # 2. Calculate the new angle based on the angular velocity and adjust the point's position
        self.orbitalCentre = centre
        self.orbitalRadius = radius
        if initialVelocity is not None:
            self.speed = getMagnitude(ORIGIN, initialVelocity)
            self.angularVelocity = self.speed / self.orbitalRadius
            if direction == "c":
                self.changeInAngle = -self.angularVelocity / RATE_OF_CALCULATIONS
            elif direction == "a":
                self.changeInAngle = self.angularVelocity / RATE_OF_CALCULATIONS
        else:
            print(self.speed)
            self.speed += 5
            self.angularVelocity = self.speed / self.orbitalRadius
            if direction == "c":
                self.changeInAngle = -self.angularVelocity / RATE_OF_CALCULATIONS
            elif direction == "a":
                self.changeInAngle = self.angularVelocity / RATE_OF_CALCULATIONS
            
        currentAngle = getTwoDAngle(self.orbitalCentre, self.pos)
        newAngle = currentAngle + self.changeInAngle
        if newAngle > (2 * math.pi):
            newAngle = newAngle - (math.pi * 2)
        newPos = [self.orbitalCentre[0] + self.orbitalRadius * math.cos(newAngle), self.orbitalCentre[1], self.orbitalCentre[2] + self.orbitalRadius * math.sin(newAngle)]
        self.pos = newPos
        
    def adjustAxesForBoosterRing(self, currentPos):
        newPos = currentPos
        if currentPos[1] != 6.5:
            newPos[1] += 1.5 / 7
        if currentPos[0] != -0.004:
            newPos[0] -= 0.004 / 7
        
        newPos[2] -= 5 / 7
            
        self.pos = newPos
    
    def adjustAxesForCollider(self, currentPos):
        newPos = currentPos
        if currentPos[1] != 12:
            newPos[1] += 4 / 8
        if currentPos[0] > 0:
            if currentPos[0] < self.xDistancePlus:
                newPos[0] += self.differencePlus / 8
        elif currentPos[0] < 0:
            if currentPos[0] > self.xDistanceMinus:
                newPos[0] -= self.differenceMinus / 8
            
        self.pos = newPos
        
    def collide(self, currentPos, differenceMatrix):
        print("Colliding")
        newPos = currentPos
        for axis in range(3):
            newPos[axis] += (differenceMatrix[axis] / 8)
        print(f"New Pos: {newPos}")
        self.pos = newPos
            
    
    def draw(self):
        '''Method that draws the hydrogen atom'''
        super().draw()


class Electron(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, BLUE, radius, initialVelocity, initialForce)
        self.charge = -SIMULATED_PROTON_CHARGE
        
    def enablePhysics(self):
        '''Method that enables the electron's physics'''
        super().enablePhysics()
    
    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        super().enableNewtonianMechanics()

    def draw(self):
        '''Method that draws the electron'''
        super().draw()

# Cuboids

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


class ChargedPlate(Cuboid):
    def __init__(self, pos, colour, size, charge):
        super().__init__(pos, colour, size)
        self.charge = charge
        
    def draw(self, alpha):
        '''Method that draws the charged plate'''
        super().draw(alpha)

# Cylinders and Frustrums

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
        


class Tube(Cylinder):
    def __init__(self, pos, colour, radius, height, axis):
        super().__init__(pos, colour, radius, height, axis)
        
    def draw(self, alpha):
        '''Method that draws the tubes'''
        super().draw(alpha)
     
# Toruses

class Collider:
    def __init__(self, pos, colour, radius, tubeRadius):
        self.pos = pos # Centre
        self.colour = colour
        self.radius = radius
        self.tubeRadius = tubeRadius
        self.object = vizshape.addTorus(radius = self.radius, tubeRadius = self.tubeRadius)
        self.started = False

    def draw(self, alpha):
        '''Method that draws the collider'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.alpha(alpha)
        
class BoosterRing:
    def __init__(self, pos, colour, radius, tubeRadius):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.tubeRadius = tubeRadius
        self.object = vizshape.addTorus(radius = self.radius, tubeRadius = self.tubeRadius)
    
    def draw(self, alpha):
        '''Method that draws the booster ring'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.alpha(alpha)
            

# Others

class SourceChamber(Cylinder):
    def __init__(self, pos, colour, radius, height, axis):
        super().__init__(pos, colour, radius, height, axis)
        self.wall = Cylinder([0, 5, -2], YELLOW, 3, 1, vizshape.AXIS_Z)
        self.nozzle = Frustrum([0, 5, -9], GREEN, 3, 5, vizshape.AXIS_Z, 0.75)
        self.sealed = False
        self.activated = False
            
    def draw(self, alpha):
        '''Method that draws the source chamber'''
        super().draw(alpha)
        if self.sealed:
            self.wall.draw(1)
        self.nozzle.draw(0.5)
        
    def seal(self):
        self.wall.object.remove()
        
    def applyPlate(self):
        self.activated = True
        self.plate = ChargedPlate([0, 9.5, -4], PURPLE, (3, 3, 5), "+")
        self.plate.draw(0.5)
        
        
class LINAC:
    def __init__(self, pos):
        self.initialLength = 3
        self.updatedPos = [0, 5, (pos[2] - 1.5)]
        self.initialGapLength = 1
        
    def draw(self):
        tubeLength = self.initialLength
        gapLength = self.initialGapLength
        pos = self.updatedPos
        for _ in range(0, 10):
            tube = Tube(pos, DARK_CYAN, 0.75, tubeLength, vizshape.AXIS_Z)
            tube.draw(0.5)
            pos = [0, 5, pos[2] - tubeLength - gapLength]
            tubeLength += 1
            gapLength += 0.1
            


    