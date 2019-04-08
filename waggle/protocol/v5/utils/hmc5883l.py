# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for HMC5883L Magnetometer
    # converted_value = float(value) / 1100 (or 980)

def convert(value):
    magx = value['lightsense_hmc5883l_hx'] / 1100
    magy = value['lightsense_hmc5883l_hy'] / 1100
    magz = value['lightsense_hmc5883l_hz'] / 980

    value['lightsense_hmc5883l_hx'] = (round(magx*1000, 3), 'mG')
    value['lightsense_hmc5883l_hy'] = (round(magy*1000, 3), 'mG')
    value['lightsense_hmc5883l_hz'] = (round(magz*1000, 3), 'mG')

    return value
