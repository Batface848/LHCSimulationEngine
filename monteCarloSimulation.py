import random
import math

def getVariance(data):
    mean = sum(data) / len(data)
    squaredDifferences = [(value - mean) ** 2 for value in data]
    variance = sum(squaredDifferences) / len(data)
    return variance
    
def obtainNormalProbabilityDensity(parameter, mean, standardDeviation):
    return (1 / (standardDeviation * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((parameter - mean) / standardDeviation) ** 2)


dataFile = open("testResultsFinalFinal.txt", "w")
higgsProbabilities = []

for i in range(1, 100001):
    initialEnergy = 13000
    chosenGeVValue = round(random.uniform(0.1, 10000.0), 1)
    possibilities = ["Elastic Scattering", "Inelastic Scattering", "Deep Inelastic Scattering", "Gluon-Gluon Fusion", "Higgs Production", "Quark-Antiquark Annihilation", "Jets Formation", "Parton-Parton Scattering", "Resonance Production"]
    collisionType = ""
    products = []
    if chosenGeVValue <= 2.0:
        collisionType = possibilities[0]
        products.append("Proton")
        products.append("Proton")
    elif chosenGeVValue >= 2.1 and chosenGeVValue <= 5.0:
        collisionType = possibilities[8]
        pionCharge = random.choice(["+", "-", "0"])
        products.append("Baryon")
        products.append("Neutron")
        products.append("Proton")
        products.append("Pion " + pionCharge)
    else:
        if chosenGeVValue >= 10.0 and chosenGeVValue <= 1000.0:
            if chosenGeVValue <= 500.0:
                if chosenGeVValue <= 30.0 and chosenGeVValue >= 20.1:
                    collisionType = possibilities[6]
                    products.append("Pion Jets")
                    products.append("Kaon Jets")
                elif chosenGeVValue >= 80.1 and chosenGeVValue <= 100:
                    collisionType = possibilities[5]
                    products.append("W + Boson")
                    products.append("W - Boson")
                    products.append("Z 0 Boson")
                elif chosenGeVValue >= 100.1 and chosenGeVValue <= 130.0:
                    if chosenGeVValue >= 124.0 and chosenGeVValue <= 126.0:
                        collisionType = possibilities[4]
                        products.append("Higgs Boson")
                        products.append("Top Quark")
                        products.append("Antitop Quark")
                        products.append("Photon")
                        products.append("Z Boson")
                        products.append("W Boson")
                        products.append("Bottom Quark")
                        products.append("Tau Lepton")
                    else:
                        collisionType = possibilities[3]
                        products.append("Top Quark")
                        products.append("Antitop Quark")
                else:
                    collisionType = possibilities[2]
                    pionCharge = random.choice(["+", "-", "0"])
                    kaonCharge = random.choice(["+", "-", "0"])
                    products.append("Pion " + pionCharge)
                    products.append("Kaon " + kaonCharge)
                    products.append("Neutrino")
                    products.append("Lepton")
            else:
                collisionType = possibilities[1]
                products.append("Pion +")
                products.append("Pion -")
                products.append("Pion 0")
                products.append("Kaon +")
                products.append("Kaon -")
                products.append("Kaon 0")
        else:
            collisionType = possibilities[7]
            products.append("Baryon Jet")
            products.append("Meson Jet")

        higgsProbabilities.append(chosenGeVValue)
        meanData = sum(higgsProbabilities) / len(higgsProbabilities)
        standardDeviationData = 0.0
        if len(higgsProbabilities) > 1:
            standardDeviationData = math.sqrt(getVariance(higgsProbabilities))
            higgsProbability = obtainNormalProbabilityDensity(125, meanData, standardDeviationData)
        else:
            higgsProbability = 1.0 if chosenGeVValue <= 126 and chosenGeVValue >= 124 else 0.0
    
    dataFile.write("Reading " + str(i) + "\n")
    dataFile.write("Collision Type: " + collisionType + "\n")
    dataFile.write("Initial Energy: " + str(initialEnergy) + "\n")
    dataFile.write("Rest Mass Energy: " + str(chosenGeVValue) + "\n")
    dataFile.write("Collision Products: " + ", ".join(products) + "\n")
    dataFile.write("Higgs Probability: " + str(higgsProbability) + "\n\n")
    
