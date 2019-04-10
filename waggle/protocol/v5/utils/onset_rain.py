# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for onset rain gauge

def convert(value):
    raw_c = value['rg3_onset_rain']
    value['rg3_onset_rain'] = (raw_c * 0.254, 'mm')

    return value
