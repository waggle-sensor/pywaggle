# Conversion for TSYS01 temperature

def convert(value, coefficients):
    assert len(coefficients) == 5
    temperature = -2.0 * float(coefficients[4]) * float(pow(10, -21)) * pow(value, 4) + \
        4.0 * float(coefficients[3]) * float(pow(10, -16)) * pow(value, 3) + \
        -2.0 * float(coefficients[2]) * float(pow(10, -11)) * pow(value, 2) + \
        1.0 * float(coefficients[1]) * float(pow(10, -6)) * value + \
        -1.5 * float(coefficients[0]) * float(pow(10, -2))
    return temperature, 'C'
