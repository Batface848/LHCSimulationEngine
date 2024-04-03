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
        self.points = []
        self.pumpTubes = []
        self.GUIObjects = []
        self.gasPump = GasPump([0, 5, 20], BLUE, (3, 10, 3))
        for i in range(3):
            pumpTube = Tube([0, 5, 13.5 - i * 10], CYAN, 0.5, 10)
            self.pumpTubes.append(pumpTube)
        self.collider = Collider([30,0,30], BLUE, 10, 3)
        self.pointOne = HydrogenAtom([3, 2, 5], SIMULATED_PROTON_RADIUS, [0, 0, 0], [-0.1, 0.6, 0.5]) # Test point
        self.points.append(self.pointOne)
        self.pointTwo = Point([2, 8, 10], BLUE, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0.1, -0.6, -0.5])
        self.points.append(self.pointTwo)
        self.centreBall = vizshape.addSphere()
        self.cameraPos = [10, 10, 10] # x, y, z
        self.cameraAngle = [0, 0, 0] # Yaw, pitch, roll
        viz.callback(viz.BUTTON_EVENT, self.getGUIState)
        self.frames = 0
        
    def main(self):
        '''Main method'''
        self.updateCam()
        self.run()

    def run(self):
        '''Runner method'''
        viz.MainView.setPosition(self.cameraPos) # Camera
        viz.MainView.setEuler(self.cameraAngle)
        self.drawSprites()
        self.drawGUI()
        for point in self.points:
            point.enablePhysics()
        self.checkPointCollisions(self.points)
        self.frames += 1

    def drawSprites(self):
        '''Method that draws all sprites required from the sprites file'''
        for point in self.points:
            point.draw()
        self.gasPump.draw()
        for tube in self.pumpTubes:
            tube.draw()
        self.collider.draw()
        
    def updateCam(self):
        '''Method that updates the camera position based on the camera's new position'''
        self.cameraPos = viz.MainView.getPosition()
        self.cameraAngle = viz.MainView.getEuler()
        self.cameraAngle[2] = 0 # Prevent camera angle tilting
        
    def drawGUI(self):
        '''Method that draws the interactive GUI on the screen'''
        self.spawnButton = viz.addButtonLabel("Add Hydrogen")
        self.spawnButton.setPosition(0.1, 0.95)
        self.GUIObjects.append(self.spawnButton)
        # self.spawnButton.color(GREEN)
        
    def getGUIState(self, obj, state):
        for obj in self.GUIObjects:
            if obj == self.spawnButton:
                if state == viz.DOWN:
                    self.spawnHydrogen()
                else:
                    pass
        
        
    def spawnHydrogen(self):
        '''Method that allows a hydrogen atom to be "pumped" from the gas pump'''
        hydrogenPoint = HydrogenAtom([0, 5, 18.5], SIMULATED_PROTON_RADIUS, [0, 0, -0.1], [0, 0, 10])
        self.points.append(hydrogenPoint)

    def checkPointCollisions(self, points):
        '''Method that checks for collisions between all points'''
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

        for i in range(len(self.distanceMatrix)):
            for j in range(i, len(self.distanceMatrix)):
                if (self.distanceMatrix[i][j] <= (points[i].radius + points[j].radius)) and (self.distanceMatrix[i][j] >= 0):
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
                    
    def checkPointCylinderCollisions(self, cylinder):
        '''Method that checks for collisions between the points and the cylinders'''
        pass
                    
                        
        



engine = LHCSimulation()
vizact.ontimer(TIME_PERIOD, engine.main) # Final line of code