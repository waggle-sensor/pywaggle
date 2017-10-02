# Conversion for HMC5883L Magnetometer

def convert(value, gain):
    converted_value = float(value) / float(gain)
    return converted_value, 'G'