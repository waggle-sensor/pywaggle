# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for HIH4030 at 5 V

# At 25 C the best linear fit is
# y = x * 30.68 (mV/%RH) + 0.958 V

def convert(value):
    raw_h = value['metsense_hih4030_humidity']
    v = float(raw_h) / 1024.0 * 5.0
    humidity = v * 30.68 + 0.958

    humidity_rounded = round(humidity, 2)
    value['metsense_hih4030_humidity'] = (humidity_rounded, '%RH')

    return value
