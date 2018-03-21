# Conversion for PMS7003 particle sensor

def convert(value):
    raw_t = value['pms7003_particle']

    value['pms7003_particle'] = (raw_t, '')

    return value
