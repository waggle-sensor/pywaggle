# Conversion for decagon soil moisture sensor

def convert(value):
    raw_d = value['dielectric']
    raw_vwc = value['volumatric_water_content']
    raw_t = value['temperature']

    value['dielectric'] = (raw_d / 50.000000, 'no unit')

    if raw_vwc < 700:
        value['volumatric_water_content'] = (raw_vwc / 100.0, 'dS/m')
    else:
        value['volumatric_water_content'] = ((raw_vwc - 700) * 5 + 700, 'dS/m')

    if raw_t < 900:
        value['temperature'] = ((raw_t - 400.0) / 10.0, 'C')
    else:
         value['temperature'] = ((raw_t - 900.0) * 5.0 + 900.0, 'C')

    return value