# Conversion to temperature in degree Celsius

# Coefficients for MF12 10k 3380 thermistor in -30 C to 110 C
# referred to http://www.cantherm.com/choosing_ntc
# T = 1 / (A + (B * ln(rt)) + (C *ln(rt)^3)), in Kelvin

# This conversion is tested in Wagman hw V3.1 ker v1.0.4

import math

def convert(value):
    assert isinstance(value, int)

    A = 0.00088570897
    B = 0.00025163902
    C = 0.00000019289731

    v_in = 1.8  # v
    R = 23000.0 # 23k ohm

    LSB = 0.0000625 # 6.25 uV for 16-bit ADC converter

    # The Wagman firmware right-shifts the value by 5 bits
    value = value << 5
    v = value * LSB

    rt = R * (Vin / V - 1)
    logrt = math.log(rt)
    temp = 1 / (A + (B * logrt) + (C * logrt * logrt * logrt))
    tempC = temp - 273.15
    return round(tempC, 2), 'C'
