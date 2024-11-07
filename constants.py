import math
from mathematicalMethods import *
import sys

# Configuration
RATE_OF_CALCULATIONS = 200 # How fast the LHCSimulation can run, Time Period = 1 / RATE_OF_CALCULATIONS
TIME_PERIOD = 1 / RATE_OF_CALCULATIONS

# Position Vectors
ORIGIN = [0, 0, 0]
LHC_CIRCUMFERENCE = 27000


# Simulated Scalars
SIMULATED_PROTON_MASS = 1
SIMULATED_PROTON_RADIUS = 0.25
SIMULATED_PROTON_CHARGE = 1.05 * 10 ** -6
SIMULATED_SPEED_OF_LIGHT = 1
SIMULATED_PERMITTIVITY = 0.01
SIMULATED_CHARGE_DENSITY = 0.1

# Physics Data
ACCELERATION_FREE_FALL = [0, -9.80665, 0]
PROTON_MASS = 1.67262192 * (10 ** -27)
PROTON_RADIUS = 0.87 * (10 ** -15)
PROTON_CHARGE = 1.6 * (10 ** -19)
PERMITTIVITY_OF_FREE_SPACE = 8.85418782 * (10 ** -12)
COULOMB_LAW_CONSTANT = 1 / (math.pi * 4 * PERMITTIVITY_OF_FREE_SPACE)
ELECTRONVOLT_JOULE_CONVERTER = 1 / (1.60 * (10 ** -19))
HYDROGEN_IONISATION_ENERGY = 13.6 * ELECTRONVOLT_JOULE_CONVERTER
SPEED_OF_LIGHT = 3 * 10 ** 8
PERMEABILITY_OF_FREE_SPACE = 4 * math.pi * (10 ** -7)

# Colours
WHITE = (255, 255, 255)
PURPLE = (3, 0, 5)
GREEN = (0, 10, 0)
BLUE = (0, 0, 10)
RED = (10, 0, 0)
CYAN = (0, 10, 10)
YELLOW = (10, 10, 0)
DARK_CYAN = (0, 4, 10)
ORANGE = (255, 1, 0)
BLACK = (0, 0, 0)
BROWN = (165, 2, 2)
TAN = (3, 2, 2)
