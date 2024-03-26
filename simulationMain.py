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
        self.collider = Collider(ORIGIN)
        self.protonOne = Proton([0, 0, 5], PURPLE, PROTON_RADIUS, self) # Test proton
        self.protonTwo = Proton([0, 0, 10], GREEN, PROTON_RADIUS, self)
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
        self.frames += 1
        viz.MainView.setPosition(self.cameraPos) # Camera
        viz.MainView.setEuler(self.cameraAngle)
        self.drawSprites()
        self.protonOne.move()
        self.protonTwo.move()

    def drawSprites(self):
        '''Method that draws all sprites required from the sprites file'''
        self.protonOne.draw()
        self.protonTwo.draw()
        
    def updateCam(self):
        '''Update camera position based on the camera's new position'''
        self.cameraPos = viz.MainView.getPosition()
        self.cameraAngle = viz.MainView.getEuler()
        self.cameraAngle[2] = 0 # Prevent camera angle tilting

engine = LHCSimulation()
vizact.ontimer(TIME_PERIOD, engine.main) # Final line of code