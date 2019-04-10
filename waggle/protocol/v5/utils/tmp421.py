# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for TMP421 temperature

def convert(value):
    raw_t = value['lightsense_tmp421']

    converted_value = 0.0
    h = (raw_t >> 8) & 0xFF
    l = raw_t & 0xFF

    bit = ((l >> 4) & 0x01) * 0.5
    converted_value += bit**4

    bit = ((l >> 5) & 0x01) * 0.5
    converted_value += bit**3

    bit = ((l >> 6) & 0x01) * 0.5
    converted_value += bit**2

    bit = ((l >> 7) & 0x01) * 0.5
    converted_value += bit

    converted_value += h
    converted_value = converted_value

    if converted_value > 128.0:
        converted_value -= 256.0

    converted_value_rounded = round(converted_value, 2)

    value['lightsense_tmp421'] = (converted_value_rounded, 'C')

    return value
