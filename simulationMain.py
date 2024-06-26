﻿# Main engine that also manages vizard initialisation
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
        self.gasPump = Cuboid([0, 5, 20], BLUE, (3, 10, 3))
        for i in range(2):
            pumpTube = Tube([0, 5, 13.5 - i * 10], CYAN, 0.5, 10, vizshape.AXIS_Z)
            self.pumpTubes.append(pumpTube)
        self.sourceChamber = SourceChamber([0, 5, -4], WHITE, 3, 5, vizshape.AXIS_Z)
        self.chamberActivated = False
        self.collider = Collider([30, 0, 30], BLUE, 10, 3)
        self.centreBall = vizshape.addSphere()
        self.cameraPos = [10, 10, 10] # x, y, z
        self.cameraAngle = [0, 0, 0] # Yaw, pitch, roll
        self.frames = 0
        self.previousFrame = None
        self.maxTime = 0.25 * RATE_OF_CALCULATIONS
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
        self.checkPointCollisions(self.points)
        self.checkPointWallCollisions(self.sourceChamber.wall)
        viz.callback(viz.BUTTON_EVENT, self.getGUIState)
        

    def drawSprites(self):
        '''Method that draws all sprites required from the sprites file'''
        for point in self.points:
            point.draw()
        self.gasPump.draw(1)
        for tube in self.pumpTubes:
            tube.draw(0.5)
        self.sourceChamber.draw(0.5)
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
        self.activateChamberButton = viz.addButtonLabel("Activate Source Chamber")
        self.activateChamberButton.setPosition(0.16, 0.875)
        self.resetButton = viz.addButtonLabel("Reset System")
        self.resetButton.setPosition(0.0975, 0.8)
        self.GUIObjects.append(self.spawnButton)
        self.GUIObjects.append(self.activateChamberButton)
        self.GUIObjects.append(self.resetButton)
        # self.spawnButton.color(GREEN)
    
    
    def getGUIState(self, obj, state):
        if obj == self.spawnButton:
            if state == viz.DOWN:
                if self.previousFrame == None:
                    self.spawnHydrogen()
                    self.previousFrame = self.frames
                    print("SPAWNED")
                else:
                    if self.frames - self.previousFrame >= self.maxTime:
                        self.spawnHydrogen()
                        self.previousFrame = self.frames
                        print("SPAWNED")
            else:
                pass
        elif obj == self.activateChamberButton:
            if state == viz.DOWN:
                self.removeCylinderWall()
            else:
                pass
        elif obj == self.resetButton:
            if state == viz.DOWN:
                self.resetSystem()
            else:
                pass
        
    def spawnHydrogen(self):
        '''Method that allows a hydrogen atom to be "pumped" from the gas pump'''
        hydrogenPoint = HydrogenAtom([0, 5, 18.5], SIMULATED_PROTON_RADIUS, [0, 0, -0.1], [0, 0, -1])
        self.points.append(hydrogenPoint)
        
    def removeCylinderWall(self):
        '''Method that removes the source chamber wall'''
        self.sourceChamber.wall.object.remove()
        self.chamberActivated = True
        

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
                    
    def checkPointWallCollisions(self, cylinder):
        '''Method that checks for collisions between the points and the walls - specifically the source chamber walls'''
        if not self.chamberActivated:
            for point in self.points:
                if (point.pos[2]) - (cylinder.pos[2]) <= (point.radius + cylinder.height / 2):
                    currentZSpeed = point.velocity[2]
                    point.oldPos[2] = point.pos[2] + (currentZSpeed / RATE_OF_CALCULATIONS)
                    
    def resetSystem(self):
        '''Method that resets the system'''
        pass
        
engine = LHCSimulation()
vizact.ontimer(TIME_PERIOD, engine.main) # Final line of code