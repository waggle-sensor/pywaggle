# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for BMP180 temperature
#
# temperature = 
# int32_t X1 = (ut - (int32_t)_bmp085_coeffs.ac6) * (
# (int32_t)_bmp085_coeffs.ac5) >> 15;
#
#   int32_t X2 = ((int32_t)_bmp085_coeffs.mc << 11) / 
# (X1+(int32_t)_bmp085_coeffs.md);
#   return X1 + X2;



def convert(value):
    # coefficients
    ac1 = 7191
    ac2 = -1005
    ac3 = -14219
    ac4 = 34229
    ac5 = 25803
    ac6 = 15820
    b1 = 6515
    b2 = 32
    mb = -32768
    mc = -11786
    md = 2331

    mode = 3

    # raw reading
    raw_t = value['metsense_bmp180_temperature']
    raw_p = value['metsense_bmp180_pressure']
    raw_p >>= (8 - mode)

    # temperature
    x1 = ((raw_t - ac6) * ac5) >> 15
    x2 = (mc << 11) / (x1 + md)
    raw_t = x1 + x2
    temperature = int(raw_t + 8) >> 4
    temperature /= 10

    # pressure
    raw_t = raw_t - 4000;
    x1 = (b2 * (int(raw_t * raw_t) >> 12)) >> 11;
    x2 = int(ac2 * raw_t) >> 11;
    x3 = x1 + x2;
    b3 = (((ac1 * 4 + x3) << mode) + 2) >> 2;
    x1 = int(ac3 * raw_t) >> 13;
    x2 = (b1 * (int(raw_t * raw_t) >> 12)) >> 16;
    x3 = ((x1 + x2) + 2) >> 2;
    b4 = (ac4 * (x3 + 32768)) >> 15;
    b7 = ((raw_p - b3) * (50000 >> mode));

    if (b7 < 0x80000000):
        p = (b7 << 1) / b4
    else:
        p = int(b7 / b4) << 1

    x1 = (int(p) >> 8) * (int(p) >> 8)
    x1 = (x1 * 3038) >> 16
    x2 = int(-7357 * p) >> 16
    pressure = int(p + ((x1 + x2 + 3791) >> 4)) / 100

    value['metsense_bmp180_temperature'] = (temperature, 'C')
    value['metsense_bmp180_pressure'] = (pressure, 'hPa')

    return value
