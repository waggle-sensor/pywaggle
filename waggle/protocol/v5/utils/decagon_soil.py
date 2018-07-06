# Conversion for decagon soil moisture sensor

def convert(value):
    # raw = value['decagon_test']
    raw_d = value['decagon_soil_dielectric']
    raw_vwc = value['decagon_soil_conductivity']
    raw_t = value['decagon_soil_temperature']

    value['decagon_soil_dielectric'] = (round(raw_d / 50.000000, 2), '')

    if raw_vwc < 700:
        value['decagon_soil_conductivity'] = (raw_vwc / 100.0, 'dS/m')
    else:
        value['decagon_soil_conductivity'] = ((raw_vwc - 700) * 5 + 700, 'dS/m')

    if raw_t < 900:
        value['decagon_soil_temperature'] = ((raw_t - 400.0) / 10.0, 'C')
    else:
         value['decagon_soil_temperature'] = ((raw_t - 900.0) * 5.0 + 900.0, 'C')

    return value
