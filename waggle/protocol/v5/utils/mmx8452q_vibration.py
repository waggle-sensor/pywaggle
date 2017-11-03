# Conversion for MMX8452Q vibration

import math

def convert(values):
    powered_values = [pow(x, 2) for x in values]
    vibration = math.sqrt(sub(powered_values))
    return vibration, 'g'

