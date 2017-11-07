# Conversion for HMC5883L Magnetometer

def convert(value):
    raw_magx = value[0x0A]['lightsense_hmc5883l_hx']
    raw_magy = value[0x0A]['lightsense_hmc5883l_hy']
    raw_magz = value[0x0A]['lightsense_hmc5883l_hz']

    raw_magx = round(raw_magx / 1100, 2)
    raw_magy = round(raw_magy / 1100, 2)
    raw_magz = round(raw_magz / 980, 2)

    # converted_value = float(value) / 1100
    return raw_magx, 'Gx', raw_magy, 'Gy', raw_magz, 'Gz'