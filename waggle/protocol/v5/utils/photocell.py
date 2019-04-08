# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for Photocellpth-kit (PDV-P8103)

# This conversion is only valid/tested in Wagman hw 3.1

# at dark it goes to 500 K ohm at 23 C
# 

# 5 V
# |
# $ photocell
# |____ V
# |
# $ 23 k ohm
# |
# GND

def convert(value):
    raw_p = value['wagman_light']
    v_in = 5.0
    r2 = 23000.0

    v = float(raw_p) / 1024.0 * 5.0
    r_photo = r2 * (v_in / v - 1)

    value['wagman_light'] = (int(r_photo), 'ohm')

    return value
