# Main engine that also manages vizard initialisation
import viz # Vizard
import vizshape # Object drawer
import vizconnect # Configuration presets
import vizact # Passes methods into Vizard task manager
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
        self.GUIObjects = []
        self.gasPump = GasPump([0, 5, 20], BLUE, (3, 10, 3))
        self.sourceChamber = SourceChamber([0, 5, 15.5], CYAN, 1, 6)
        self.collider = Collider([30,0,30], BLUE, 10, 3)
        self.pointOne = HydrogenAtom([10, 0, 10], SIMULATED_PROTON_RADIUS, [0, 0, 0], [-1, 0, 0]) # Test point
        self.points.append(self.pointOne)
        self.pointTwo = HydrogenAtom([-10, 0, 10], SIMULATED_PROTON_RADIUS, [0, 0, 0], [1, 0, 0])
        self.points.append(self.pointTwo)
        self.centreBall = vizshape.addSphere()
        self.cameraPos = [10, 10, 10] # x, y, z
        self.cameraAngle = [0, 0, 0] # Yaw, pitch, roll
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
        for point in self.points:
            point.enablePhysics()
        self.checkPointCollisionDetection()
        self.drawGUI()
        viz.callback(viz.BUTTON_EVENT, self.getGUIState)
        self.frames += 1

    def drawSprites(self):
        '''Method that draws all sprites required from the sprites file'''
        for point in self.points:
            point.draw()
        self.gasPump.draw()
        self.sourceChamber.draw()
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
        hydrogenPoint = HydrogenAtom([0, 5, 18.5], SIMULATED_PROTON_RADIUS, [0, 0, -0.01], [0, 0, -1])
        self.points.append(hydrogenPoint)

    def checkPointCollisionDetection(self):
        '''Method that checks for collision detection between all points'''
        self.distanceMatrix = []
        for i in range(len(self.points)):
            rowVector = []
            for j in range(len(self.points)):
                if i == j:
                    rowVector.append(-1)
                else:
                    distance = getMagnitude(self.points[i].pos, self.points[j].pos)
                    rowVector.append(distance)
            self.distanceMatrix.append(rowVector)

        for i in range(len(self.distanceMatrix)):
            for j in range(i, len(self.distanceMatrix)):
                if self.distanceMatrix[i][j] <= (self.points[i].radius + self.points[j].radius) and self.distanceMatrix[i][j] >= 0:
                    print("COLLIDE")
                    
                        
        



engine = LHCSimulation()
vizact.ontimer(TIME_PERIOD, engine.main) # Final line of code