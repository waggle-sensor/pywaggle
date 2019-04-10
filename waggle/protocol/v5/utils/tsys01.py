# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
# Conversion for TSYS01 temperature

def convert(value):
    # coefficients
    c4 = 5714
    c3 = 7338
    c2 = 15996
    c1 = 22746
    c0 = 34484


    # assert len(coefficients) == 5
    raw_t = value['metsense_tsys01_temperature']
    raw_t >>= 8

    temperature = (-2.0e-21 * c4 * raw_t**4 +
                   4.0e-16 * c3 * raw_t**3 +
                   -2.0e-11 * c2 * raw_t**2 +
                   1.0e-6 * c1 * raw_t +
                   -1.5e-2 * c0)

    temperature_rounded = round(temperature, 2)
    value['metsense_tsys01_temperature'] = (temperature_rounded, 'C')

    return value
