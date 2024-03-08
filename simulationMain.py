# Main engine that also manages vizard initialisation
import viz # Vizard
import vizshape # Object drawer
import vizconnect # Configuration presets
from sprites import *
from constants import *

# Main simulation class
class LHCSimulation():
    def __init__(self):
        self.proton = Proton(ORIGIN, PURPLE, 1) # Test proton
        self.cameraPos = (0, 10, 0)
        self.cameraAttitude = (0, 90, 0)
		
    def run(self):
        '''Main runner method'''
        viz.MainView.setPosition(self.cameraPos) # Camera
        viz.MainView.setEuler(self.cameraAttitude) # Pitch, yaw, tilt
        vizshape.addGrid() # Adds a grid for easier testing
        self.drawSprites()
        viz.window.setFullscreen() # Makes testing easier
        viz.fov(90) # Field of view
        viz.go()
		
    def drawSprites(self):
        '''Method that draws all sprites required from the sprites file'''
        self.proton.draw()

engine = LHCSimulation()
engine.run()