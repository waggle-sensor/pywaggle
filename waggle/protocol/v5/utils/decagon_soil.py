# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for decagon soil moisture sensor

def convert(value):
    # raw = value['decagon_test']
    raw_d = value['5te_soil_dielectric']
    raw_vwc = value['5te_soil_conductivity']
    raw_t = value['5te_soil_temperature']

    value['5te_soil_dielectric'] = (round(raw_d / 50.000000, 2), '')

    if raw_vwc < 700:
        value['5te_soil_conductivity'] = (raw_vwc / 100.0, 'dS/m')
    else:
        value['5te_soil_conductivity'] = ((raw_vwc - 700) * 5 + 700, 'dS/m')

    if raw_t < 900:
        value['5te_soil_temperature'] = ((raw_t - 400.0) / 10.0, 'C')
    else:
         value['5te_soil_temperature'] = ((raw_t - 900.0) * 5.0 + 900.0, 'C')

    return value
