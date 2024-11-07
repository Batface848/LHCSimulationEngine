# Main engine that also manages vizard initialisation
import viz # Vizard
import vizshape # Object drawer
import vizconnect # Configuration presets
import vizact # Passes methods into Vizard task manager
import vizmenu
import random
from sprites2 import *
from constants import *
from mathematicalMethods import *
import random



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
        self.products = []
        self.higgsProbabilities = []
        self.pumpTubes = []
        self.GUIObjects = []
        self.connectionTubes = []
        self.circuitGrid = []
        self.gasPump = Cuboid([0, 5, 20], BLUE, (3, 10, 3))
        for i in range(2):
            pumpTube = Tube([0, 5, 13.5 - i * 10], CYAN, 0.5, 10, vizshape.AXIS_Z)
            self.pumpTubes.append(pumpTube)
        
        self.LINAC = LINAC([0, 5, -11.5])
        self.mainWire = Wire([0, 0.5, -44.25], BLUE, (0.25, 0.25, 75.5))
        self.circuitGrid.append(self.mainWire)
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
        # self.centreBall = vizshape.addSphere()
        self.collided = False
        self.readingNumber = 1
        self.textObjects = []
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
        if not self.collided:
            for point in self.points:
                point.enablePhysics()
        
            for point in self.points.copy():
                if point.pos[2] > 18.5:
                    point.object.remove()
                    self.points.remove(point)
         
                if point.pos[2] < -95 and type(point) == Proton:
                    if not point.completedLINAC:
                        point.completedLINAC = True
                        point.teleport = True
            
                if type(point) == Proton and point.boosted:
                    if self.points.index(point) == 0:
                        point.endBoostZCord = -69
                    else:
                        point.endboostZCord = -131
                   
            if not self.sourceChamber.activated:
                self.obtainCoulombForce(self.points)
        # self.checkPointCollisions(self.points)
        # self.checkPointWallCollisions(self.sourceChamber)
                self.obtainCoulombWallForce(self.sourceChamber)
        
            self.ableToCollide = False
            for point in self.points:
                if type(point) == Proton:
                    if point.goingThroughCollider and point.speed > 3500:
                        self.ableToCollide = True
                else:
                    pass
        
            if self.ableToCollide:
                print("ABLE TO COLLIDE")
                self.obtainDistanceMatrix(self.points)
                print(self.distanceMatrix)
                if self.distanceMatrix[1][0] < 30:
                    self.collideProtons(self.points[0], self.points[1])
        
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
        for wire in self.circuitGrid:
            wire.draw(0.5)
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
        self.resetSystemButton = viz.addButtonLabel("Reset System")
        self.resetSystemButton.setPosition(0.095, 0.725)
        self.nextTestButton = viz.addButtonLabel("Obtain Next Readings")
        self.nextTestButton.setPosition(0.14, 0.65)
        self.GUIObjects.append(self.spawnButton)
        self.GUIObjects.append(self.sealChamberButton)
        self.GUIObjects.append(self.activateChamberButton)
        self.GUIObjects.append(self.resetSystemButton)
        self.GUIObjects.append(self.nextTestButton)
        self.readingsLog = CollisionDataBox(self.readingNumber)
        self.readingsLog.draw()
        # self.spawnButton.color(GREEN)
    
    def getGUIState(self, obj, state):
        if obj == self.spawnButton:
            if state == viz.DOWN:
                if self.previousFrame == None:
                    self.spawnHydrogen()
                    self.previousFrame = self.frames
                else:
                    if self.frames - self.previousFrame >= self.maxTime:
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
                
        elif obj == self.resetSystemButton:
            if state == viz.DOWN:
                self.resetSystem()
            else:
                pass
                
        elif obj == self.nextTestButton:
            if state == viz.DOWN:
                self.nextTest()
            else:
                pass
        
    def spawnHydrogen(self):
        '''Method that allows a hydrogen atom to be "pumped" from the gas pump'''
        if not self.sourceChamber.sealed and len(self.points) < 2:
            hydrogenPoint = HydrogenAtom([0, 5, 18.5], SIMULATED_PROTON_RADIUS, [0, 0, -0.1], [0, 0, 0])
            self.points.append(hydrogenPoint)
       
    def sealChamber(self):
        '''Method that seals the source chamber'''
        self.sourceChamber.seal()
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
                distanceFromEndTerminal = -95 - point.pos[2]
                point.terminal = "-"
                forceMagnitude = self.obtainLINACElectricField(distanceFromEndTerminal)
                point.force = [0, 0, forceMagnitude]

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
                    
    
    def collideProtons(self, proton1, proton2):
        self.collided = True
        self.readingsLog.initialGEVTextObject.object.message("Initial Energy: 13,000GeV")
        midpoint = findMidpoint(proton1.pos, proton2.pos)
        chosenGeVValue = 0.1
        # chosenGeVValue = round(random.uniform(0.1, 3000.0), 1)
        possibilities = ["Elastic Scattering", "Inelastic Scattering", "Deep Inelastic Scattering", "Gluon-Gluon Fusion", "Higgs Production", "Quark-Antiquark Annihilation", "Jets Formation", "Parton-Parton Scattering", "Resonance Production"]
        for point in self.points.copy():
            point.object.remove()
            self.points.remove(point)
        self.readingsLog.GEVUsedTextObject.object.message("Rest Mass Energy: " + str(chosenGeVValue) + "GeV")
        if chosenGeVValue <= 2.0:
            self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[0])
            proton1Vector = [0, 0, 0]
            proton2Vector = [0, 0, 0]
            finalPosOne = [0, 0, 0]
            finalPosTwo = [0, 0, 0]
            for axis in range(3):
                proton1Vector[axis] = midpoint[axis] - proton1.pos[axis]
                proton2Vector[axis] = midpoint[axis] - proton2.pos[axis]
            magnitudeOne = getMagnitude(ORIGIN, proton1Vector)
            magnitudeTwo = getMagnitude(ORIGIN, proton2Vector)
            for axis in range(3):
                finalPosOne[axis] = midpoint[axis] - (proton1Vector[axis] / magnitudeOne)
                finalPosTwo[axis] = midpoint[axis] - (proton2Vector[axis] / magnitudeTwo)
            realProtonOne = Proton(finalPosOne, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0], self.bRing, self.collider)
            realProtonTwo = Proton(finalPosTwo, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0], self.bRing, self.collider)
            realProtonOne.draw()
            realProtonTwo.draw()
            fakeProtonOne = Proton([22.5, 57, -179], 2, [0, 0, 0], [0, 0, 0], self.bRing, self.collider)
            fakeProtonTwo = Proton([22.5, 44, -179], 2, [0, 0, 0], [0, 0, 0], self.bRing, self.collider)
            fakeProtonOne.draw()
            fakeProtonTwo.draw()
            protonTextOne = Text("Proton", [-22.5, 57, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
            protonTextTwo = Text("Proton", [-22.5, 44, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
            protonTextOne.write()
            protonTextTwo.write()
            self.products = [realProtonOne, realProtonTwo, fakeProtonOne, fakeProtonTwo]
            self.textObjects.append(protonTextOne)
            self.textObjects.append(protonTextTwo)
        elif chosenGeVValue >= 2.1 and chosenGeVValue <= 5.0:
            self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[8])
            baryon = Baryon(midpoint, 1, [0, 0, 0], [0, 0, 0])
            baryon.draw(0.5)
            protonProductPos = [midpoint[0] + 2, midpoint[1] + 2, midpoint[2] + 2]
            protonProduct = Point(protonProductPos, PURPLE, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
            protonProduct.draw()
            neutronPos = [midpoint[0] - 1, midpoint[1] - 2, midpoint[2]]
            neutron = Neutron(pos = neutronPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
            neutron.draw()
            pionPos = [midpoint[0] - 3, midpoint[1], midpoint[2] - 1]
            pion = Pion(pos = pionPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0], charge = random.choice(["+", "-", "0"]))
            pion.draw()
            fakeBaryon = Baryon([22.5, 62, -179], 2, [0, 0, 0], [0, 0, 0])
            fakeBaryon.draw(1)
            fakeProton = Proton([22.5, 54, -179], 1, [0, 0, 0], [0, 0, 0], self.bRing, self.collider)
            fakeProton.draw()
            fakeNeutron = Neutron([22.5, 46, -179], 1, [0, 0, 0], [0, 0, 0])
            fakeNeutron.draw()
            fakePion = Pion([22.5, 38, -179], 1, [0, 0, 0], [0, 0, 0], charge = "+")
            fakePion.draw()
            baryonText = Text("Baryon", [-22.5, 62, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
            protonText = Text("Proton", [-22.5, 54, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
            neutronText = Text("Neutron", [-22.5, 46, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
            pionText = Text(("Pion " + pion.charge), [-22.5, 38, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
            baryonText.write()
            protonText.write()
            neutronText.write()
            pionText.write()
            self.products = [baryon, protonProduct, neutron, pion, fakeBaryon, fakeProton, fakeNeutron, fakePion]
            self.textObjects.append(baryonText)
            self.textObjects.append(protonText)
            self.textObjects.append(neutronText)
            self.textObjects.append(pionText)
        else:
            if chosenGeVValue >= 10.0 and chosenGeVValue <= 1000.0:
                if chosenGeVValue <= 500.0: 
                    if chosenGeVValue <= 30.0 and chosenGeVValue >= 20.1:
                        self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[6])
                        explosionPoint = Point(midpoint, RED, 1, [0, 0, 0], [0, 0, 0])
                        explosionPoint.draw()
                        self.products.append(explosionPoint)
                        for i in range(5):
                            pionPos = [midpoint[0] + (1 + i * 1), midpoint[1] - (2 + i * 1), midpoint[2]]
                            pion = Pion(pionPos, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0], charge = random.choice(["+", "-", "0"]))
                            pion.draw()
                            self.products.append(pion)
                            kaonPos = [midpoint[0] - (2 + i * 1), midpoint[1] + (2 + i * 1), midpoint[2]]
                            kaon = Kaon(kaonPos, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            kaon.draw()
                            self.products.append(kaon)
                        fakePion = Pion([22.5, 57, -179], 2, [0, 0, 0], [0, 0, 0], charge = "0")
                        fakeKaon = Kaon([22.5, 44, -179], 2, [0, 0, 0], [0, 0, 0])
                        fakePion.draw()
                        fakeKaon.draw()
                        fakePionText = Text("Pion Jets", [-22.5, 57, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        fakeKaonText = Text("Kaon Jets", [-22.5, 44, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        fakePionText.write()
                        fakeKaonText.write()
                        self.products.append(fakePion)
                        self.products.append(fakeKaon)
                        self.textObjects.append(fakePionText)
                        self.textObjects.append(fakeKaonText)
                    elif chosenGeVValue >= 80.1 and chosenGeVValue <= 100.0:
                        self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[5])
                        explosionPoint = Point(midpoint, YELLOW, 1, [0, 0, 0], [0, 0, 0])
                        explosionPoint.draw()
                        WPlusPos = [midpoint[0], midpoint[1], midpoint[2] + 3]
                        WPlus = Point(pos = WPlusPos, colour = RED, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                        WPlus.draw()
                        WNegativePos = [midpoint[0] - 1, midpoint[1] + 1, midpoint[2]]
                        WNegative = Point(WNegativePos, RED, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                        WNegative.draw()
                        ZZeroPos = [midpoint[0] - 2, midpoint[1] - 1, midpoint[2] + 1]
                        ZZero = Point(ZZeroPos, ORANGE, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                        ZZero.draw()
                        fakeWPlus = Point([22.5, 60, -179], RED, 2, [0, 0, 0], [0, 0, 0])
                        fakeWPlus.draw()
                        fakeWNegative = Point([22.5, 50, -179], RED, 2, [0, 0, 0], [0, 0, 0])
                        fakeWNegative.draw()
                        fakeZZero = Point([22.5, 40, -179], ORANGE, 2, [0, 0, 0], [0, 0, 0])
                        fakeZZero.draw()
                        WPlusText = Text("W + Boson", [-22.5, 60, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        WNegativeText = Text("W - Boson", [-22.5, 50, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        ZZeroText = Text("Z 0 Boson", [-22.5, 40, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        WPlusText.write()
                        WNegativeText.write()
                        ZZeroText.write()
                        self.products = [explosionPoint, WPlus, WNegative, ZZero, fakeWPlus, fakeWNegative, fakeZZero]
                        self.textObjects.append(WPlusText)
                        self.textObjects.append(WNegativeText)
                        self.textObjects.append(ZZeroText)
                    elif chosenGeVValue >= 100.1 and chosenGeVValue <= 130.0:
                        if chosenGeVValue >= 124.0 and chosenGeVValue <= 126.0:
                            self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[4])
                            higgsBoson = Point(midpoint, GREEN, 1, [0, 0, 0], [0, 0, 0])
                            higgsBoson.draw()
                            finalPosOne = [midpoint[0] + 2, midpoint[1], midpoint[2] + 2]
                            finalPosTwo = [midpoint[0] - 1, midpoint[1] - 3, midpoint[2] + 1]
                            finalPosThree = [midpoint[0] + 1, midpoint[1] - 3, midpoint[2] + 2]
                            finalPosFour = [midpoint[0] + 3, midpoint[1] + 1, midpoint[2] - 1]
                            finalPosFive = [midpoint[0] + 2, midpoint[1] - 3, midpoint[2] - 3]
                            finalPosSix = [midpoint[0] + 3, midpoint[1] + 1, midpoint[2] - 1]
                            finalPosSeven = [midpoint[0], midpoint[1] - 2, midpoint[2] - 3]
                            topQuark = Point(finalPosOne, YELLOW, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            antitopQuark = Point(finalPosTwo, DARK_CYAN, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            topQuark.draw()
                            antitopQuark.draw()
                            photon = Point(finalPosThree, BLACK, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            photon.draw()
                            zBoson = Point(finalPosFour, ORANGE, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            zBoson.draw()
                            wBoson = Point(pos = finalPosFive, colour = RED, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                            wBoson.draw()
                            bottomQuark = Point(pos = finalPosSix, colour = BROWN, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                            bottomQuark.draw()
                            tauLepton = Lepton(pos = finalPosSeven, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                            tauLepton.draw()
                            fakeHiggsBoson = Point([22.5, 65.6, -179], GREEN, 2, [0, 0, 0], [0, 0, 0])
                            faketopQuark = Point([22.5, 61.2, -179], YELLOW, 1, [0, 0, 0], [0, 0, 0])
                            fakeAntitopQuark = Point([22.5, 56.8, -179], DARK_CYAN, 1, [0, 0, 0], [0, 0, 0])
                            fakePhoton = Point([22.5, 52.4, -179], BLACK, 1, [0, 0, 0], [0, 0, 0])
                            fakeZBoson = Point([22.5, 48, -179], ORANGE, 1, [0, 0, 0], [0, 0, 0])
                            fakeWBoson = Point([22.5, 43.6, -179], colour = RED, radius = 1, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                            fakeBottomQuark = Point(pos = [22.5, 39.2, -179], colour = BROWN, radius = 1, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                            fakeTauLepton = Lepton(pos = [22.5, 34.8, -179], radius = 1, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                            fakeHiggsBoson.draw()
                            faketopQuark.draw()
                            fakeAntitopQuark.draw()
                            fakePhoton.draw()
                            fakeZBoson.draw()
                            fakeWBoson.draw()
                            fakeBottomQuark.draw()
                            fakeTauLepton.draw()
                            HiggsText = Text("Higgs Boson", [-22.5, 65.6, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            TopTextOne = Text("Top Quark", [-22.5, 61.2, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            AntiTopTextTwo = Text("Antitop Quark", [-22.5, 56.8, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            PhotonText = Text("Photon", [-22.5, 52.4, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            ZBosonText = Text("Z Boson", [-22.5, 48, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            WBosonText = Text("W Boson", [-22.5, 43.6, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            BottomQuarkText = Text("Bottom Quark", [-22.5, 39.2, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            TauLeptonText = Text("Tau Lepton", [-22.5, 34.8, -179], WHITE, viz.ALIGN_CENTER, 4, [-1, 1, 1])
                            HiggsText.write()
                            TopTextOne.write()
                            AntiTopTextTwo.write()
                            PhotonText.write()
                            ZBosonText.write()
                            WBosonText.write()
                            BottomQuarkText.write()
                            TauLeptonText.write()
                            self.textObjects.append(HiggsText)
                            self.textObjects.append(TopTextOne)
                            self.textObjects.append(AntiTopTextTwo)
                            self.textObjects.append(PhotonText)
                            self.textObjects.append(ZBosonText)
                            self.textObjects.append(WBosonText)
                            self.textObjects.append(BottomQuarkText)
                            self.textObjects.append(TauLeptonText)
                            self.products = [higgsBoson, fakeHiggsBoson, topQuark, antitopQuark, faketopQuark, fakeAntitopQuark, photon, fakePhoton, zBoson, fakeZBoson, wBoson, fakeWBoson, bottomQuark, fakeBottomQuark, tauLepton, fakeTauLepton]
                        else:
                            self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[3])
                            explosionPoint = Point(midpoint, BLUE, 1, [0, 0, 0], [0, 0, 0])
                            explosionPoint.draw()
                            finalPosOne = [midpoint[0] + 2, midpoint[1], midpoint[2] + 2]
                            finalPosTwo = [midpoint[0] - 1, midpoint[1] - 3, midpoint[2] + 1]
                            topQuark = Point(finalPosOne, YELLOW, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            antitopQuark = Point(finalPosTwo, DARK_CYAN, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                            topQuark.draw()
                            antitopQuark.draw()
                            faketopQuark = Point([22.5, 57, -179], YELLOW, 2, [0, 0, 0], [0, 0, 0])
                            fakeAntitopQuark = Point([22.5, 44, -179], DARK_CYAN, 2, [0, 0, 0], [0, 0, 0])
                            faketopQuark.draw()
                            fakeAntitopQuark.draw()
                            TopTextOne = Text("Top Quark", [-22.5, 57, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                            AntiTopTextTwo = Text("Antitop Quark", [-22.5, 44, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                            TopTextOne.write()
                            AntiTopTextTwo.write()
                            self.products = [explosionPoint, topQuark, antitopQuark, faketopQuark, fakeAntitopQuark]
                    else:
                        self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[2])
                        explosionPoint = Point(midpoint, BROWN, 1, [0, 0, 0], [0, 0, 0])
                        explosionPoint.draw()
                        pionPos = [midpoint[0] - 2, midpoint[1], midpoint[2]]
                        pion = Pion(pos = pionPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0], charge = random.choice(["+", "-", "0"]))
                        pion.draw()
                        kaonPos = [midpoint[0] + 3, midpoint[1] + 1, midpoint[2] + 2]
                        kaon = Kaon(kaonPos, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                        kaon.draw()
                        neutrinoPos = [midpoint[0] + 1, midpoint[1] - 3, midpoint[2] - 2]
                        neutrino = Neutrino(pos = neutrinoPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                        neutrino.draw()
                        leptonPos = [midpoint[0], midpoint[1] - 2, midpoint[2] - 3]
                        lepton = Lepton(pos = leptonPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                        lepton.draw()
                        fakePion = Pion([22.5, 62, -179], 2, [0, 0, 0], [0, 0, 0], charge = "0")
                        fakePion.draw()
                        fakeKaon = Kaon([22.5, 54, -179], 2, [0, 0, 0], [0, 0, 0])
                        fakeKaon.draw()
                        fakeNeutrino = Neutrino([22.5, 46, -179], 2, [0, 0, 0], [0, 0, 0])
                        fakeNeutrino.draw()
                        fakeLepton = Lepton([22.5, 38, -179], 2, [0, 0, 0], [0, 0, 0])
                        fakeLepton.draw()
                        pionText = Text("Pion " + pion.charge, [-22.5, 62, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        kaonText = Text("Kaon " + random.choice(["+", "-", "0"]), [-22.5, 54, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        neutrinoText = Text("Neutrino", [-22.5, 46, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        leptonText = Text("Lepton", [-22.5, 38, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                        pionText.write()
                        kaonText.write()
                        neutrinoText.write()
                        leptonText.write()
                        self.textObjects.append(pionText)
                        self.textObjects.append(kaonText)
                        self.textObjects.append(neutrinoText)
                        self.textObjects.append(leptonText)
                        self.products = [explosionPoint, pion, kaon, neutrino, lepton, fakePion, fakeKaon, fakeNeutrino, fakeLepton]
                else:
                    self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[1])
                    explosionPoint = Point(midpoint, DARK_CYAN, 1, [0, 0, 0], [0, 0, 0])
                    explosionPoint.draw()
                    pionPlusPos = [midpoint[0] - 3, midpoint[1], midpoint[2] - 1]
                    pionPlus = Pion(pos = pionPlusPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0], charge = "+")
                    pionPlus.draw()
                    pionNegativePos = [midpoint[0] + 1, midpoint[1], midpoint[2] - 3]
                    pionNegative = Pion(pos = pionNegativePos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0], charge = "-")
                    pionNegative.draw()
                    pionZeroPos = [midpoint[0] + 1, midpoint[1] - 3, midpoint[2] - 2]
                    pionZero = Pion(pos = pionZeroPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0], charge = "0")
                    pionZero.draw()
                    kaonPlusPos = [midpoint[0], midpoint[1] - 1, midpoint[2] - 3]
                    kaonPlus = Kaon(pos = kaonPlusPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                    kaonPlus.draw()
                    kaonNegativePos = [midpoint[0] - 1, midpoint[1] + 1, midpoint[2] - 1]
                    kaonNegative = Kaon(pos = kaonNegativePos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                    kaonNegative.draw()
                    kaonZeroPos = [midpoint[0] - 3, midpoint[1] - 1, midpoint[2] - 2]
                    kaonZero = Kaon(pos = kaonZeroPos, radius = SIMULATED_PROTON_RADIUS, initialVelocity = [0, 0, 0], initialForce = [0, 0, 0])
                    kaonZero.draw()
                    fakePionPlus = Pion([22.5, 64.3, -179], 2, [0, 0, 0], [0, 0, 0], charge = "+")
                    fakePionPlus.draw()
                    fakePionNegative = Pion([22.5, 58.6, -179], 2, [0, 0, 0], [0, 0, 0], charge = "-")
                    fakePionNegative.draw()
                    fakePionZero = Pion([22.5, 52.9, -179], 2, [0, 0, 0], [0, 0, 0], charge = "0")
                    fakePionZero.draw()
                    fakeKaonPlus = Kaon([22.5, 47.2, -179], 2, [0, 0, 0], [0, 0, 0])
                    fakeKaonPlus.draw()
                    fakeKaonNegative = Kaon([22.5, 41.5, -179], 2, [0, 0, 0], [0, 0, 0])
                    fakeKaonNegative.draw()
                    fakeKaonZero = Kaon([22.5, 35.8, -179], 2, [0, 0, 0], [0, 0, 0])
                    fakeKaonZero.draw()
                    pionPlusText = Text("Pion +", [-22.5, 64.3, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                    pionMinusText = Text("Pion -", [-22.5, 58.6, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                    pionZeroText = Text("Pion 0", [-22.5, 52.9, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                    kaonPlusText = Text("Kaon +", [-22.5, 47.2, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                    kaonMinusText = Text("Kaon -", [-22.5, 41.5, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                    kaonZeroText = Text("Kaon 0", [-22.5, 35.8, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                    pionPlusText.write()
                    pionMinusText.write()
                    pionZeroText.write()
                    kaonPlusText.write()
                    kaonMinusText.write()
                    kaonZeroText.write()
                    self.textObjects.append(pionPlusText)
                    self.textObjects.append(pionMinusText)
                    self.textObjects.append(pionZeroText)
                    self.textObjects.append(kaonPlusText)
                    self.textObjects.append(kaonMinusText)
                    self.textObjects.append(kaonZeroText)
                    self.products = [explosionPoint, pionPlus, pionNegative, pionZero, kaonPlus, kaonNegative, kaonZero, fakePionPlus, fakePionNegative, fakePionZero, fakeKaonPlus, fakeKaonNegative, fakeKaonZero]
            else:
                self.readingsLog.collisionTypeTextObject.object.message("Collision Type: " + possibilities[7])
                explosionPoint = Point(midpoint, ORANGE, 1, [0, 0, 0], [0, 0, 0])
                explosionPoint.draw()
                self.products.append(explosionPoint)
                for i in range(5):
                    baryonPos = [midpoint[0] + (2 + i * 1), midpoint[1] + (1 + i * 1), midpoint[2]]
                    baryon = Baryon(baryonPos, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                    baryon.draw(1)
                    self.products.append(baryon)
                    mesonPos = [midpoint[0] - (1 + i * 1), midpoint[1], midpoint[2] + (3 + i * 1)]
                    meson = Meson(mesonPos, SIMULATED_PROTON_RADIUS, [0, 0, 0], [0, 0, 0])
                    meson.draw()
                    self.products.append(meson)
                fakeBaryon = Baryon([22.5, 57, -179], 2, [0, 0, 0], [0, 0, 0])
                fakeMeson = Meson([22.5, 44, -179], 2, [0, 0, 0], [0, 0, 0])
                fakeBaryon.draw(1)
                fakeMeson.draw()
                fakeBaryonText = Text("Baryon Jet", [-22.5, 57, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                fakeMesonText = Text("Meson Jet", [-22.5, 44, -179], WHITE, viz.ALIGN_CENTER, 5, [-1, 1, 1])
                fakeBaryonText.write()
                fakeMesonText.write()
                self.products.append(fakeMeson)
                self.products.append(fakeBaryon)
                self.textObjects.append(fakeMesonText)
                self.textObjects.append(fakeBaryonText)
                        
        monteCarloProbability = 1 - abs(chosenGeVValue - 125) / 125
        if monteCarloProbability < 0:
            self.higgsProbabilities.append(0.0)
        else:
            self.higgsProbabilities.append(monteCarloProbability)
        meanProbability = round(sum(self.higgsProbabilities) / len(self.higgsProbabilities), 10)
        self.readingsLog.higgsProbabilityTextObject.object.message("Higgs Probability: " + str(meanProbability))
        
    def resetSystem(self):
        for point in self.points:
            point.object.remove()
        for point in self.products:
            point.object.remove()
        self.points = []
        self.products = []
        self.sourceChamber.reset()
        self.readingsLog.collisionTypeTextObject.object.message("Collision Type: ")
        self.readingsLog.initialGEVTextObject.object.message("Initial Energy: ")
        self.readingsLog.GEVUsedTextObject.object.message("Rest Mass Energy: ")
        self.readingsLog.productsTextObject.object.message("Collision Products: ")
        for textobj in self.textObjects.copy():
            textobj.object.remove()
            self.textObjects.remove(textobj)
        
    def nextTest(self):
        self.resetSystem()
        self.readingNumber += 1
        self.readingsLog.updateCount(self.readingNumber)
                
    def obtainCoulombForce(self, points):
        self.obtainDistanceMatrix(points)
        for i in range(len(self.distanceMatrix) - 1):
            if self.distanceMatrix[i][i + 1] == 0:
                continue

            # Coulomb's Law Application
            if self.distanceMatrix[i][i + 1] < 4:
                electricForceMagnitude = (COULOMB_LAW_CONSTANT * ((SIMULATED_PROTON_CHARGE * SIMULATED_PROTON_CHARGE)) / (self.distanceMatrix[i][i + 1] ** 2)) # In this case, we are only dealing with hydrogen atoms and protons, which have the same charge
                vector = [points[i + 1].pos[axis] - points[i].pos[axis] for axis in range(3)]
                vectorMagnitude = getMagnitude(ORIGIN, vector)
                unitVector = [vector[axis] / vectorMagnitude for axis in range(3)]
                collisionNormal = getThreeDAngle(points[i].pos, points[i + 1].pos)
                changeInMomentum = electricForceMagnitude * RATE_OF_CALCULATIONS
                quartiles = getQuartiles(points[i].pos, points[i + 1].pos)
                points[i].pos[0] -= changeInMomentum * quartiles[0] * math.cos(collisionNormal[1]) * math.sin(collisionNormal[0]) / (points[i].mass * RATE_OF_CALCULATIONS)
                points[i + 1].pos[0] += changeInMomentum * quartiles[0] * math.cos(collisionNormal[1]) * math.sin(collisionNormal[0]) / (points[i + 1].mass * RATE_OF_CALCULATIONS)
                points[i].pos[1] -= changeInMomentum * quartiles[1] * math.sin(collisionNormal[1]) / (points[i].mass * RATE_OF_CALCULATIONS)
                points[i + 1].pos[1] += changeInMomentum * quartiles[1] * math.sin(collisionNormal[1]) / (points[i + 1].mass * RATE_OF_CALCULATIONS)
                points[i].pos[2] -= changeInMomentum * quartiles[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]) / (points[i].mass * RATE_OF_CALCULATIONS)
                points[i + 1].pos[2] += changeInMomentum * quartiles[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]) / (points[i + 1].mass * RATE_OF_CALCULATIONS)

    def obtainCoulombWallForce(self, chamber):
        for point in self.points:
            if not chamber.activated:
                if abs(point.pos[2] - chamber.nozzle.pos[2]) < (1 + chamber.nozzle.height / 2):
                    electricForceMagnitude = (COULOMB_LAW_CONSTANT * ((SIMULATED_PROTON_CHARGE * SIMULATED_PROTON_CHARGE)) / ((point.pos[2] - chamber.nozzle.pos[2] - chamber.nozzle.height / 2) ** 2))
                    collisionNormal = getThreeDAngle(point.pos, chamber.nozzle.pos)
                    changeInMomentum = electricForceMagnitude * RATE_OF_CALCULATIONS
                    quartiles = getQuartiles(point.pos, chamber.nozzle.pos)
                    point.pos[2] -= changeInMomentum * quartiles[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]) / (point.mass * RATE_OF_CALCULATIONS)
                    
        if chamber.sealed:
            for point in self.points:					
               if abs(point.pos[2] - chamber.wall.pos[2]) < (1 + chamber.wall.height / 2):
                    electricForceMagnitude = (COULOMB_LAW_CONSTANT * ((SIMULATED_PROTON_CHARGE * SIMULATED_PROTON_CHARGE)) / ((point.pos[2] - chamber.wall.pos[2] - chamber.wall.height / 2) ** 2))
                    collisionNormal = getThreeDAngle(point.pos, chamber.wall.pos)
                    changeInMomentum = electricForceMagnitude * RATE_OF_CALCULATIONS
                    quartiles = getQuartiles(point.pos, chamber.wall.pos)
                    point.pos[2] -= changeInMomentum * quartiles[2] * math.cos(collisionNormal[1]) * math.cos(collisionNormal[0]) / (point.mass * RATE_OF_CALCULATIONS)

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
                    
    
    def obtainLINACElectricField(self, distance):
        cylinderRadius = 0.75
        eFieldMagnitude = (SIMULATED_PROTON_CHARGE * distance) / (4 * math.pi * PERMITTIVITY_OF_FREE_SPACE * ((cylinderRadius ** 2 + distance ** 2) ** (3 / 2)))
        return eFieldMagnitude * 100

engine = LHCSimulation()
vizact.ontimer(TIME_PERIOD, engine.main) # Final line of code`