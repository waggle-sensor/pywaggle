# Conversion for HMC5883L Magnetometer
    # converted_value = float(value) / 1100 (or 980)

def convert(value):
    raw_magx = value['lightsense_hmc5883l_hx']
    raw_magy = value['lightsense_hmc5883l_hy']
    raw_magz = value['lightsense_hmc5883l_hz']

    value['lightsense_hmc5883l_hx'] = (raw_magx / 1100, 'Gx')
    value['lightsense_hmc5883l_hy'] = (raw_magy / 1100, 'Gy')
    value['lightsense_hmc5883l_hz'] = (raw_magz / 980, 'Gz')

    return value
