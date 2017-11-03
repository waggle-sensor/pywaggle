# Conversion for ACS 764

# Assumed configurations are
# AVG_POINT = 32 points
# GAIN_RANGE = 15.66 mA per LSB
# FAULT_LEVEL = 0

# Maximum measurement is 8000 mA

def convert(value):
    LSB = 15.66
    return value * LSB, 'mA'