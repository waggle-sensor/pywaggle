# Conversion for HMC5883L Magnetometer
    # converted_value = float(value) / 1100 (or 980)

def convert(value):
    magx = value['lightsense_hmc5883l_hx'] / 1100
    magy = value['lightsense_hmc5883l_hy'] / 1100
    magz = value['lightsense_hmc5883l_hz'] / 980

    magx_rounded = round(magx*1000, 3)
    magy_rounded = round(magy*1000, 3)
    magz_rounded = round(magz*1000, 3)

    value['lightsense_hmc5883l_hx'] = (magx_rounded, 'mGx')
    value['lightsense_hmc5883l_hy'] = (magy_rounded, 'mGy')
    value['lightsense_hmc5883l_hz'] = (magz_rounded, 'mGz')

    return value
