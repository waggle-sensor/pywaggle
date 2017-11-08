# Conversion for ACS 764

# Assumed configurations are
# AVG_POINT = 32 points
# GAIN_RANGE = 15.66 mA per LSB
# FAULT_LEVEL = 0

# Maximum measurement is 8000 mA

def convert(value):
    LSB = 15.66

    value['wagman_current_wagman'] = []
    value['wagman_current_nc'] = []
    value['wagman_current_ep'] = []
    value['wagman_current_cs'] = []
    value['wagman_current_port4'] = []
    value['wagman_current_port5'] = []

    value['wagman_current_wagman'].extend((value['wagman_current_wagman'] * LSB, 'mA'))
    value['wagman_current_nc'].extend((value['wagman_current_nc'] * LSB, 'mA'))
    value['wagman_current_ep'].extend((value['wagman_current_ep'] * LSB, 'mA'))
    value['wagman_current_cs'].extend((value['wagman_current_cs'] * LSB, 'mA'))
    value['wagman_current_port4'].extend((value['wagman_current_port4'] * LSB, 'mA'))
    value['wagman_current_port5'].extend((value['wagman_current_port5'] * LSB, 'mA'))

    return value