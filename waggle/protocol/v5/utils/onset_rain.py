# Conversion for onset rain gauge

def convert(value):
    raw_c = value['rg3_onset_rain']
    value['rg3_onset_rain'] = (raw_c * 0.254, 'mm')

    return value
