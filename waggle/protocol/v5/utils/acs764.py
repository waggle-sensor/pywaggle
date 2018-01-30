# Conversion for ACS 764

# Assumed configurations are
# AVG_POINT = 32 points
# GAIN_RANGE = 15.66 mA per LSB
# FAULT_LEVEL = 0

# Maximum measurement is 8000 mA

def convert(value):
    LSB = 15.66

    values = {
        'wagman_current_wagman': (value['wagman_current_wagman'] * LSB, 'mA'),
        'wagman_current_nc': (value['wagman_current_nc'] * LSB, 'mA'),
        'wagman_current_ep': (value['wagman_current_ep'] * LSB, 'mA'),
        'wagman_current_cs': (value['wagman_current_cs'] * LSB, 'mA'),
        'wagman_current_port4': (value['wagman_current_port4'] * LSB, 'mA'),
        'wagman_current_port5': (value['wagman_current_port5'] * LSB, 'mA'),
    }
    return values