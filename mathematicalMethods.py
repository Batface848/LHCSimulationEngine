import math
import numpy as np
import scipy as sp
import sympy as symp
from constants import *

def getTwoDAngle(cordOne, cordTwo): 
    '''Method that finds the 2D angle'''
    deltaZ = cordTwo[2] - cordOne[2] # abs() required because direction is obtained through getQuartiles and this method is to simply find the magnitude of angle
    deltaX = cordTwo[0] - cordOne[0]
    
    if deltaX == 0:
        if deltaZ >= 0:
            return 3 * math.pi / 2
        if deltaZ < 0:
            return math.pi / 2
    angle = math.atan2(deltaZ, deltaX)
    if angle >= 0:
        return angle
    else:
        return (math.pi * 2 + angle)
        
def getThreeDAngle(cordOne, cordTwo):
    '''Method that finds the 3D angle'''
    deltaX = abs(cordTwo[0] - cordOne[0])
    deltaY = abs(cordTwo[1] - cordOne[1])
    deltaZ = abs(cordTwo[2] - cordOne[2])

    # Check angle from x to z
    if deltaZ != 0:
        alpha = math.atan(deltaX / deltaZ)
    else:
        alpha = math.pi / 2

    xzMagnitude = math.sqrt(deltaX ** 2 + deltaZ ** 2)

    if (deltaX != 0) or (deltaZ != 0):
        beta = math.atan(deltaY / xzMagnitude)
    else:
        beta = math.pi / 2

    return [alpha, beta, 0]
        

def getMagnitude(cordOne, cordTwo):
    '''Method that finds the magnitude between two points'''
    diff = [0, 0, 0]
    for d in range(3):
        diff[d] = cordTwo[d] - cordOne[d]
    return math.sqrt(diff[0] ** 2 + diff[1] ** 2 + diff[2] ** 2)

def getQuartiles(cordOne, cordTwo):
    '''Method that gets the resultant direction of motion of the point depending on the quartile'''
    multiplier = [1, 1, 1]
    if cordOne[0] > cordTwo[0]:
        multiplier[0] = -1
    if cordOne[1] > cordTwo[1]:
        multiplier[1] = -1
    if cordOne[2] > cordTwo[2]:
        multiplier[2] = -1

    return multiplier

def vectorCrossProduct(vector1, vector2):
    crossProduct = []
    crossProduct.append((vector1[1] * vector2[2]) - (vector1[2] * vector2[1]))
    crossProduct.append((vector1[2] * vector2[0]) - (vector1[0] * vector2[2]))
    crossProduct.append((vector1[0] * vector2[1]) - (vector1[1] * vector2[0]))

    return crossProduct
    
def findMidpoint(cordOne, cordTwo):
    midpoint = [0, 0, 0]
    for axis in range(3):
        midpoint[axis] = (cordOne[axis] + cordTwo[axis]) / 2
    
    return midpoint

def getCylinderSurfaceArea(radius, height):
    return 2 * math.pi * radius * height


