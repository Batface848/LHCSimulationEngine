

# Main engine that also manages vizard initialisation
import viz # Vizard
import vizshape # Object drawer
import vizconnect # Configuration presets
import vizact # Passes methods into Vizard task manager
import random
from sprites import *
from constants import *
from mathematicalMethods import *



# Only ran once
viz.window.setFullscreen() # Makes testing easier
viz.fov(90) # Field of view
viz.vsync(0) # Disabling vsync limits the maximum number of calculations to the frame rate of the display.
viz.go()

# Main simulation class
class LHCSimulation:
    def __init__(self):
        vizshape.addGrid(step = 1.0) # Adds a grid for easier testing
        viz.MainView.collision(viz.OFF)
        self.frames = 0
        self.timePeriod = self.frames // RATE_OF_CALCULATIONS
        self.points = []
        self.pumpTubes = []
        self.GUIObjects = []
        self.connectionTubes = []
        self.gasPump = Cuboid([0, 5, 20], BLUE, (3, 10, 3))
        for i in range(2):
            pumpTube = Tube([0, 5, 13.5 - i * 10], CYAN, 0.5, 10, vizshape.AXIS_Z)
            self.pumpTubes.append(pumpTube)
        self.LINAC = LINAC([0, 5, -11.5])
        self.sourceChamber = SourceChamber([0, 5, -4], WHITE, 3, 5, vizshape.AXIS_Z)
        self.bRing = BoosterRing([-31, 6.5, -100], YELLOW, 30, 2.5)
        self.connectionTube1 = Tube([24, 8, -69], CYAN, 0.75, 110, vizshape.AXIS_X)
        self.connectionTube2 = Tube([-80, 8, -131], CYAN, 0.75, 98, vizshape.AXIS_X)
        self.connectionTubes.append(self.connectionTube1)
        self.connectionTubes.append(self.connectionTube2)
        self.collider = Collider([0, 12, -180], WHITE, 140, 6)
        self.cameraPos = [0, 8, 100] # x, y, z
        self.cameraAngle = [0, 0, 0] # Yaw, pitch, roll
        self.previousFrame = None
        self.maxTime = 0.2 * RATE_OF_CALCULATIONS
        # self.testProtonTwo = Proton([-3, 0, 0], 0.25, [0.01, 0, 0], [0, 0, 0])
        # self.points.append(self.testProtonTwo)
        self.collisionStartPos = []
        self.collisionMidpoint = [0, 0, 0]
        self.collided = False
        self.drawGUI()
        
    def main(self):
        '''Main method'''
        self.updateCam()
        self.run()

    def run(self):
        '''Runner method'''
        self.frames += 1
        viz.MainView.setPosition(self.cameraPos) # Camera
        viz.MainView.setEuler(self.cameraAngle)
        self.drawSprites()
        for point in self.points:
            point.enablePhysics()
            print(f"Point {self.points.index(point)}: {point.pos}")
        
        for point in self.points.copy():
            if point.pos[2] > 18.5:
                point.object.remove()
                self.points.remove(point)
            
            if point.pos[2] < -95 and type(point) == Proton and not point.completedLINAC:
                point.completedLINAC = True
                
        if self.collided:
            for point in self.points:
                if not point.collided:
                    if point.goingThroughCollider and point.speed >= 6065:
                        point.collided = True
                        
            allCollided = all(point.collided for point in self.points)
            if allCollided:
                for i in range(len(self.points)):
                    if len(self.collisionStartPos) < 2:
                        print("Appending")
                        self.collisionStartPos.append(self.points[i].pos.copy())
                    else:
                        pass
                if len(self.collisionStartPos) == 2:
                    self.collisionMidpoint = findMidpoint(self.collisionStartPos[0], self.collisionStartPos[1])
                    print(f"CollisionStartPoints: {self.collisionStartPos}")
                    print(f"Midpoint: {self.collisionMidpoint}")
                    for i in range(len(self.points)):
                        xDifference = self.collisionMidpoint[0] - self.collisionStartPos[i][0]
                        zDifference = self.collisionMidpoint[2] - self.collisionStartPos[i][2]
                        differenceMatrix = [xDifference, 0, zDifference]
                        if self.points[i].pos != self.collisionMidpoint:
                            self.points[i].collide(self.points[i].pos, differenceMatrix)
                            print(f"Old Frame CollisionStartPoints: {self.collisionStartPos}")
                        else:
                            pass
                            
        self.checkPointCollisions(self.points)
        self.checkPointWallCollisions(self.sourceChamber)
        viz.callback(viz.BUTTON_EVENT, self.getGUIState)
        

    def drawSprites(self):
        '''Method that draws all sprites required from the sprites file'''
        for point in self.points:
            point.draw()
        self.gasPump.draw(1)
        for tube in self.pumpTubes:
            tube.draw(0.5)
        for tube in self.connectionTubes:
            tube.draw(0.5)
        self.LINAC.draw()
        self.sourceChamber.draw(0.5)
        self.bRing.draw(0.5)
        self.collider.draw(0.5)
        
    def updateCam(self):
        '''Method that updates the camera position based on the camera's new position'''
        self.cameraPos = viz.MainView.getPosition()
        self.cameraAngle = viz.MainView.getEuler()
        self.cameraAngle[2] = 0 # Prevent camera angle tilting
        
    def drawGUI(self):
        '''Method that draws the interactive GUI on the screen'''
        self.spawnButton = viz.addButtonLabel("Add Hydrogen")
        self.spawnButton.setPosition(0.1, 0.95)
        self.sealChamberButton = viz.addButtonLabel("Seal Source Chamber")
        self.sealChamberButton.setPosition(0.14, 0.875)
        self.activateChamberButton = viz.addButtonLabel("Activate Chamber")
        self.activateChamberButton.setPosition(0.12, 0.8)
        self.startColliderButton = viz.addButtonLabel("Start Collider")
        self.startColliderButton.setPosition(0.0945, 0.725)
        self.collideButton = viz.addButtonLabel("COLLIDE!")
        self.collideButton.setPosition(0.08, 0.650)
        self.GUIObjects.append(self.spawnButton)
        self.GUIObjects.append(self.sealChamberButton)
        self.GUIObjects.append(self.activateChamberButton)
        self.GUIObjects.append(self.collideButton)
        # self.spawnButton.color(GREEN)
    
    def getGUIState(self, obj, state):
        if obj == self.spawnButton:
            if state == viz.DOWN:
                if self.previousFrame == None:
                    self.spawnHydrogen()
                    self.previousFrame = self.frames
                else:
                    if self.frames - self.previousFrame >= self.maxTime * 0.4:
                        self.spawnHydrogen()
                        self.previousFrame = self.frames
            else:
                pass
        elif obj == self.sealChamberButton:
            if state == viz.DOWN:
                self.sealChamber()
            else:
                pass
                
        elif obj == self.activateChamberButton:
            if state == viz.DOWN:
                self.activateChamber()                
            else:
                pass
                
        elif obj == self.startColliderButton:
            if state == viz.DOWN:
                self.startCollider()
            else:
                pass
                
        elif obj == self.collideButton:
            if state == viz.DOWN:
                self.collideProtons()
            else:
                pass
        
    def spawnHydrogen(self):
        '''Method that allows a hydrogen atom to be "pumped" from the gas pump'''
        if not self.sourceChamber.sealed and len(self.points) < 2:
            hydrogenPoint = HydrogenAtom([0, 5, 18.5], SIMULATED_PROTON_RADIUS, [0, 0, -0.1], [0, 0, 0])
            self.points.append(hydrogenPoint)
       
    def sealChamber(self):
        '''Method that seals the source chamber'''
        self.sourceChamber.sealed = True
        for point in self.points.copy(): # Must be a copy of self.points
            if (point.pos[2] + point.radius) > (self.sourceChamber.wall.pos[2] - self.sourceChamber.wall.height / 2):
                point.object.remove()
                self.points.remove(point)
        
        for point in self.points.copy(): # Replace hydrogen atoms with protons
            point.oldPos = point.pos
            newPoint = Proton(point.pos, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0], self.bRing, self.collider)
            self.points.remove(point)
            point.object.remove()
            self.points.append(newPoint)
            
    def activateChamber(self):
        '''Method that activates the chamber'''
        if self.sourceChamber.sealed and not self.sourceChamber.activated and len(self.points) > 1:
            self.sourceChamber.applyPlate()
            for point in self.points:
                point.force = [0, 0, -100]
                
    def startCollider(self):
        '''Method that starts the collider'''
        if self.sourceChamber.sealed and self.sourceChamber.activated and not self.collider.started:
            for point in self.points:
                if point.boosting == True:
                    self.collider.started = True
                    if self.points.index(point) < len(self.points) // 2:
                        point.deflectionDirection = "+"
                    else:
                        point.deflectionDirection = "-"

    def obtainDistanceMatrix(self, points):
        '''Method that calculates the distance between all points and returns a matrix'''
        self.distanceMatrix = []
        for i in range(len(points)):
            rowVector = []
            for j in range(len(points)):
                if i == j:
                    rowVector.append(-1)
                else:
                    distance = getMagnitude(points[i].pos, points[j].pos)
                    rowVector.append(distance)
            self.distanceMatrix.append(rowVector)
            
        
    def checkPointCollisions(self, points):
        '''Method that checks for collisions between all points'''
        self.obtainDistanceMatrix(points)
        for i in range(len(self.distanceMatrix)):
            for j in range(i, len(self.distanceMatrix)):
                if (self.distanceMatrix[i][j] <= (points[i].radius + points[j].radius)) and (self.distanceMatrix[i][j] >= 0):
                    if not self.collided:
                        # Reversed coordinate geometry 
                        collisionNormal = getThreeDAngle(points[i].pos, points[j].pos) # Size of the normal angle of the collision plane
                        relativeVelocity = [abs(points[i].velocity[0] - points[j].velocity[0]), abs(points[i].velocity[1] - points[j].velocity[1]), abs(points[i].velocity[2] - points[j].velocity[2])]
                        resultantSpeed = (relativeVelocity[0] * math.cos(collisionNormal[1]) * math.sin(collisionNormal[0])) + (relativeVelocity[1] * math.sin(collisionNormal[1])) + (relativeVelocity[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]))# Sum individual components of relative velocity relative to the normal
                        changeInMomentum = ((points[i].mass * points[j].mass) / (points[i].mass + points[j].mass)) * resultantSpeed * 2
                        quartiles = getQuartiles(points[i].pos, points[j].pos) # Determine deflection direction for each point
                        # Change in momentum / mass = Change in Displacement / Change In Time
                        points[i].pos[0] -= changeInMomentum * quartiles[0] * math.cos(collisionNormal[1]) * math.sin(collisionNormal[0]) / (points[i].mass * RATE_OF_CALCULATIONS)
                        points[j].pos[0] += changeInMomentum * quartiles[0] * math.cos(collisionNormal[1]) * math.sin(collisionNormal[0]) / (points[j].mass * RATE_OF_CALCULATIONS)
                        points[i].pos[1] -= changeInMomentum * quartiles[1] * math.sin(collisionNormal[1]) / (points[i].mass * RATE_OF_CALCULATIONS)
                        points[j].pos[1] += changeInMomentum * quartiles[1] * math.sin(collisionNormal[1]) / (points[j].mass * RATE_OF_CALCULATIONS)
                        points[i].pos[2] -= changeInMomentum * quartiles[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]) / (points[i].mass * RATE_OF_CALCULATIONS)
                        points[j].pos[2] += changeInMomentum * quartiles[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]) / (points[j].mass * RATE_OF_CALCULATIONS)
                    else:
                        for point in self.points.copy():
                            self.points.remove(point)
                            point.object.remove()
                    
                        self.newBall = vizshape.addSphere()
                        self.newBall.setPosition(self.collisionMidpoint)
                    


    def checkPointWallCollisions(self, chamber):
        '''Method that checks for collisions between the points and the walls (and the nozzle) - specifically the source chamber walls'''
        for point in self.points:
            if not chamber.activated:
                if abs((point.pos[2] - (chamber.nozzle.pos[2])) <= (point.radius + chamber.nozzle.height / 2)):
                    currentZSpeed = point.velocity[2]
                    point.oldPos[2] = point.pos[2] + (currentZSpeed / RATE_OF_CALCULATIONS)
                    
        if chamber.sealed:
            for point in self.points:
                if abs((point.pos[2]) - (chamber.wall.pos[2])) <= (point.radius + chamber.wall.height / 2):
                    currentZSpeed = point.velocity[2]
                    point.oldPos[2] = point.pos[2] + (currentZSpeed / RATE_OF_CALCULATIONS)
                    
    def collideProtons(self):
        self.collided = True
        
engine = LHCSimulation()
vizact.ontimer(TIME_PERIOD, engine.main) # Final line of code

