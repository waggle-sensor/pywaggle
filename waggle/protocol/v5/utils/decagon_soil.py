# Conversion for decagon soil moisture sensor

def convert(value):
    # raw = value['decagon_test']
    raw_d = value['soil_dielectric']
    raw_vwc = value['soil_conductivity']
    raw_t = value['soil_temperature']

    value['soil_dielectric'] = (round(raw_d / 50.000000, 2), '')

    if raw_vwc < 700:
        value['soil_conductivity'] = (raw_vwc / 100.0, 'dS/m')
    else:
        value['soil_conductivity'] = ((raw_vwc - 700) * 5 + 700, 'dS/m')

    if raw_t < 900:
        value['soil_temperature'] = ((raw_t - 400.0) / 10.0, 'C')
    else:
         value['soil_temperature'] = ((raw_t - 900.0) * 5.0 + 900.0, 'C')

    return value
