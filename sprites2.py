# Sprite files that contain all sprites required for simulation

import viz
import vizshape
import vizmenu
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
        self.terminal = None
        
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
        self.teleport = False
        self.orbitingRing = False
        self.boosted = False
        self.passingThroughConnectionTube = False
        self.goingThroughCollider = False
        self.endBoostZCord = -131

    def enablePhysics(self):
        '''Method that enables the hydrogen atom's physics'''
        if self.teleport:
            self.speed = getMagnitude(ORIGIN, self.velocity)
            if self.speed >= 2500:
                self.boosted = True
            else:
                self.boosted = False
            if self.boosted:
                if not self.goingThroughCollider:
                    if self.passingThroughConnectionTube:
                        self.enterMainCollider()
                    else:
                        if abs(self.pos[2] - self.endBoostZCord) < 5:
                            self.passingThroughConnectionTube = True
                            if self.endBoostZCord == -69:
                                self.pos = [-31, 8, -69]
                            else:
                                self.pos = [-31, 8, -131]
                        else:
                            self.moveThroughBoosterRing()
                else:
                    self.moveThroughCollider()
            else:
                self.moveThroughBoosterRing()
        else:
            self.enableNewtonianMechanics()
            
    def moveThroughBoosterRing(self):
        '''Method that moves the proton through the booster ring'''
        if self.pos[2] <= -95 and self.pos[2] >= -105 and self.pos[0] >= -3 and self.pos[0] <= 3:
            inAccelerator = True
        else:
            inAccelerator = False
        if not self.orbitingRing:
            if self.pos[1] < 6.5 and self.pos[0] > -0.004:
                self.adjustAxesForBoosterRing(self.pos)
            else:
                self.orbitingRing = True
        else:
            if inAccelerator:
                eForce = self.boosterRing.obtainSynchrotronElectricField()
                eAcceleration = (eForce / self.mass)
                eSpeed = -self.speed + eAcceleration * (TIME_PERIOD)
                zDisplacement = eSpeed * (TIME_PERIOD)
                newZ = self.pos[2] + zDisplacement
                self.pos[2] = newZ
                self.acceleration = [0, 0, eAcceleration]
                self.velocity = [0, 0, eSpeed]
            else:
                self.numericalCircularMotion(self.boosterRing.pos, 31, "c")
                
    def moveThroughCollider(self):
        if self.pos[2] <= -313 and self.pos[2] >= -327 and self.pos[0] >= -25 and self.pos[0] <= 25:
            acceleratingInCollider = True
        else:
            acceleratingInCollider = False
        if acceleratingInCollider:
            eForce = self.collider.obtainColliderElectricField()
            eAcceleration = (eForce / self.mass)
            if self.endBoostZCord == -69:
                eSpeed = -self.speed + eAcceleration * (TIME_PERIOD)
                xDisplacement = eSpeed * (TIME_PERIOD)
                newX = self.pos[0] + xDisplacement
                self.pos[0] = newX
                self.acceleration = [eAcceleration, 0, 0]
                self.velocity = [eSpeed, 0, 0]
            else:
                eSpeed = -self.speed + eAcceleration * (TIME_PERIOD)
                xDisplacement = abs(eSpeed * (TIME_PERIOD))
                newX = self.pos[0] + xDisplacement
                self.pos[0] = newX
                self.acceleration = [eAcceleration, 0, 0]
                self.velocity = [eSpeed, 0, 0]
                
        else:
            if self.endBoostZCord == -69:
                self.numericalCircularMotion(self.collider.pos, 142, "c")
            else:
                self.numericalCircularMotion(self.collider.pos, 138, "a")
                
    def enterMainCollider(self):
        '''Method that moves the proton through the connection tubes'''
        if self.endBoostZCord == -69:
            xDisplacement = self.speed * (TIME_PERIOD)
            newX = self.pos[0] + xDisplacement
            if newX > 100:
                self.passingThroughConnectionTube = False
                self.goingThroughCollider = True
            else:
                self.pos[0] = newX
        else:
            xDisplacement = self.speed * (TIME_PERIOD)
            newX = self.pos[0] - xDisplacement
            if newX < -134:
                self.passingThroughConnectionTube = False
                self.goingThroughCollider = True
            else:
                self.pos[0] = newX
        

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
        
    def numericalCircularMotion(self, centre, radius, direction, initialSpeed = None):
        '''Method that manages circular motion in the booster ring and the actual collider using a numerical method'''
        # 1. Calculate angular velocity from the starting velocity and the orbital radius
        # 2. Calculate the new angle based on the angular velocity and adjust the point's position
        self.orbitalCentre = centre
        self.orbitalRadius = radius
        self.angularVelocity = self.speed / self.orbitalRadius
        if direction == "c":
            self.changeInAngle = -self.angularVelocity / RATE_OF_CALCULATIONS
        elif direction == "a":
            self.changeInAngle = self.angularVelocity / RATE_OF_CALCULATIONS
        # print(f"Speed {self.speed} changeInAngle {self.changeInAngle}")
        currentAngle = getTwoDAngle(self.orbitalCentre, self.pos)
        newAngle = currentAngle + self.changeInAngle
        if newAngle > (2 * math.pi):
            newAngle = newAngle - (math.pi * 2)
        newPos = [self.orbitalCentre[0] + self.orbitalRadius * math.cos(newAngle), self.orbitalCentre[1], self.orbitalCentre[2] + self.orbitalRadius * math.sin(newAngle)]
        self.pos = newPos
        print(self.speed)
        
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
    
    def draw(self):
        '''Method that draws the hydrogen atom'''
        super().draw()


class Neutron(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, DARK_CYAN, radius, initialVelocity, initialForce)
        
    def enablePhysics(self):
        '''Method that enables the electron's physics'''
        super().enablePhysics()
    
    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        super().enableNewtonianMechanics()

    def draw(self):
        '''Method that draws the electron'''
        super().draw()
        
class Baryon(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, GREEN, radius, initialVelocity, initialForce)
        
    def draw(self, alpha):
        super().draw()
        self.object.alpha(alpha)
        
    
    def enablePhysics(self):
        super().enablePhysics()
        
    def enableNewtonianMechanics(self):
        super().enableNewtonianMechanics()
        
class Pion(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce, charge):
        super().__init__(pos, YELLOW, radius, initialVelocity, initialForce)
        self.charge = charge
            
    def draw(self):
        super().draw()
    
    def enablePhysics(self):
        super().enablePhysics()
        
    def enableNewtonianMechanics(self):
        super().enableNewtonianMechanics()
        
class Meson(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, BROWN, radius, initialVelocity, initialForce)
    
    def enablePhysics(self):
        '''Method that enables the electron's physics'''
        super().enablePhysics()
    
    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        super().enableNewtonianMechanics()

    def draw(self):
        '''Method that draws the electron'''
        super().draw()
        
class Kaon(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, BLACK, radius, initialVelocity, initialForce)
    
    def enablePhysics(self):
        '''Method that enables the electron's physics'''
        super().enablePhysics()
    
    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        super().enableNewtonianMechanics()

    def draw(self):
        '''Method that draws the electron'''
        super().draw()
        
class Neutrino(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, CYAN, radius, initialVelocity, initialForce)
    
    def enablePhysics(self):
        '''Method that enables the electron's physics'''
        super().enablePhysics()
    
    def enableNewtonianMechanics(self):
        '''Method that moves the point using the calculated resultant force'''
        super().enableNewtonianMechanics()

    def draw(self):
        '''Method that draws the electron'''
        super().draw()
        
class Lepton(Point):
    def __init__(self, pos, radius, initialVelocity, initialForce):
        super().__init__(pos, TAN, radius, initialVelocity, initialForce)
    
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

class Wire(Cuboid):
	def __init__(self, pos, colour, size):
		super().__init__(pos, colour, size)
		
	def draw(self, alpha):
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
        self.electricAccelerator = Cuboid([0, 12, -320], CYAN, (50, 14, 14))

    def draw(self, alpha):
        '''Method that draws the collider'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.alpha(alpha)
        self.electricAccelerator.draw(0.3)
        
    def obtainColliderElectricField(self):
        cuboid = self.electricAccelerator.size
        eFieldMagnitude = (SIMULATED_PROTON_CHARGE * -1) / (cuboid[1] * cuboid[1] * PERMITTIVITY_OF_FREE_SPACE)
        return eFieldMagnitude * 2
        
class BoosterRing:
    def __init__(self, pos, colour, radius, tubeRadius):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.tubeRadius = tubeRadius
        self.object = vizshape.addTorus(radius = self.radius, tubeRadius = self.tubeRadius)
        self.electricAccelerator = Cuboid([0, 6.5, -100], CYAN, (6, 6, 10))
    
    def draw(self, alpha):
        '''Method that draws the booster ring'''
        self.object.setPosition(self.pos)
        self.object.color((self.colour))
        self.object.alpha(alpha)
        self.electricAccelerator.draw(0.3)
        
    def obtainSynchrotronElectricField(self):
        cuboid = self.electricAccelerator.size
        eFieldMagnitude = (SIMULATED_PROTON_CHARGE * -1) / (cuboid[1] * cuboid[1] * PERMITTIVITY_OF_FREE_SPACE)
        return eFieldMagnitude * 2
        
# Others

class SourceChamber(Cylinder):
    def __init__(self, pos, colour, radius, height, axis):
        super().__init__(pos, colour, radius, height, axis)
        self.nozzle = Frustrum([0, 5, -9], GREEN, 3, 5, vizshape.AXIS_Z, 0.75)
        self.sealed = False
        self.activated = False
            
    def draw(self, alpha):
        '''Method that draws the source chamber'''
        super().draw(alpha)
        self.nozzle.draw(0.5)
        
    def reset(self):
        if self.sealed:
            print("Remove object")
            self.wall.object.remove()
            self.sealed = False
        if self.activated:
            self.plate.object.remove()
            self.activated = False
    
    def seal(self):
        self.sealed = True
        self.wall = Cylinder([0, 5, -1.5], YELLOW, 3, 0.25, vizshape.AXIS_Z)
        self.wall.draw(1)
        
    def applyPlate(self):
        self.activated = True
        self.plate = ChargedPlate([0, 0.5, -4], PURPLE, (3, 3, 5), "+")
        self.plate.draw(0.5)
        
class LINAC:
    def __init__(self, pos):
        self.initialLength = 3
        self.updatedPos = [0, 5, (pos[2] - 1.5)]
        self.initialGapLength = 1
        self.tubes = []
        self.wires = []
        self.checkpoints = []
        self.updateObjects()
        
    def draw(self):
        for tube in self.tubes:
            tube.draw(0.5)
        
        for wire in self.wires:
            wire.draw(0.5)
    
    def updateObjects(self):
        tubeLength = self.initialLength
        gapLength = self.initialGapLength
        pos = self.updatedPos
        for i in range(0, 10):
            tube = Tube(pos, DARK_CYAN, 0.75, tubeLength, vizshape.AXIS_Z)
            tube.draw(0.5)
            if i < 9:
                wire = Wire([0, 2.375, (pos[2] - (tubeLength / 2) - (gapLength / 4))], BLUE, (0.25, 3.75, 0.25))
                self.wires.append(wire)
            pos = [0, 5, pos[2] - tubeLength - gapLength]
            tubeLength += 1
            gapLength += 0.1
            
class CollisionDataBox(Cuboid):
    def __init__(self, readingNumber):
        super().__init__([0, 70, -180], BLUE, (100, 100, 1))
        self.heading = "Reading " + str(readingNumber)
        self.collisionType = "Collision Type: "
        self.initialGEV = "Initial Energy: "
        self.GEVUsed = "Rest Mass Energy: "
        self.products = "Collision Products: "
        self.higgsProbability = "Higgs Probability: "
        self.text = [self.heading, self.collisionType, self.initialGEV]
        self.headerTextObject = Text(self.heading, [0, 110, -179], WHITE, viz.ALIGN_CENTER, 10, [-1, 1, 1])
        self.collisionTypeTextObject = Text(self.collisionType, [45, 100, -179], WHITE, viz.ALIGN_LEFT_TOP, 5, [-1, 1, 1])
        self.initialGEVTextObject = Text(self.initialGEV, [45, 90, -179], WHITE, viz.ALIGN_LEFT_TOP, 5, [-1, 1, 1])
        self.GEVUsedTextObject = Text(self.GEVUsed, [45, 80, -179], WHITE, viz.ALIGN_LEFT_TOP, 5, [-1, 1, 1])
        self.productsTextObject = Text(self.products, [45, 70, -179], WHITE, viz.ALIGN_LEFT_TOP, 5, [-1, 1, 1])
        self.higgsProbabilityTextObject = Text(self.higgsProbability, [45, 30, -179], WHITE, viz.ALIGN_LEFT_TOP, 5, [-1, 1, 1])
        
    
    def draw(self):
        super().draw(1)
        self.headerTextObject.write()
        self.collisionTypeTextObject.write()
        self.initialGEVTextObject.write()
        self.GEVUsedTextObject.write()
        self.productsTextObject.write()
        self.higgsProbabilityTextObject.write()
    
    def updateCount(self, count):
        self.headerTextObject.object.message("Reading " + str(count))

class Text:
    def __init__(self, text, pos, colour, alignment, size, scale):
        self.text = text
        self.pos = pos
        self.colour = colour
        self.alignment = alignment
        self.size = size
        self.scale = scale
        self.object = viz.addText3D(self.text, pos = self.pos)
        
    def write(self):
        self.object.color(self.colour)
        self.object.alignment(self.alignment)
        self.object.fontSize(self.size)
        self.object.setScale(self.scale)

        