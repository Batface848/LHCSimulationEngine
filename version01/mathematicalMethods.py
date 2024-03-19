import math

def getTwoDAngle(cordOne, cordTwo): 
    '''Method that finds the 2D angle'''
    deltaY = abs(cordTwo[1] - cordOne[1]) # abs() required because direction is obtained through getQuartiles and this method is to simply find the magnitude of angle
    deltaX = abs(cordTwo[0] - cordOne[0])

    if deltaX == 0:
        return math.pi / 2
    else:
        return math.atan(deltaY / deltaX)

def getMagnitude(cordOne, cordTwo):
    '''Method that finds the ma[gnitude between two points'''
    diff = [0, 0, 0]
    for d in range(3):
        diff[d] = cordTwo[d] - cordOne[d]
    return math.sqrt(diff[0] ** 2 + diff[1] ** 2 + diff[2] ** 2)

def getQuartiles(cordOne, cordTwo):
    '''Method that gets the resultant direction of motion of the point depending on the quartile'''
    if (cordTwo[1] >= cordOne[1]) and (cordTwo[0] >= cordOne[0]):
        return [1, 1]
    elif (cordTwo[1] >= cordOne[1]) and (cordTwo[0] < cordOne[0]):
        return [-1, 1]
    elif (cordTwo[1] < cordOne[1]) and (cordTwo[0] >= cordOne[0]):
        return [1, -1]
    elif (cordTwo[1] < cordOne[1]) and (cordTwo[0] < cordOne[0]):
        return [-1, -1]
