# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion to temperature in degree Celsius

# Coefficients for MF12 10k 3380 thermistor in -30 C to 110 C
# referred to http://www.cantherm.com/choosing_ntc
# T = 1 / (A + (B * ln(rt)) + (C *ln(rt)^3)), in Kelvin

# This conversion is tested in Wagman hw V3.1 ker v1.0.4

import math


def convert(value):
    for p, f in conversions:
        value[p] = f(value[p])

    return value


def calculation_others(value):
    A = 0.00088570897
    B = 0.00025163902
    C = 0.00000019289731

    Vin = 1.8  # v
    R = 23000.0 # 23k ohm

    LSB = 0.0000625 # 6.25 uV for 16-bit ADC converter

    # The Wagman firmware right-shifts the value by 5 bits
    value = value << 5
    V = value * LSB

    try:
        rt = R * (Vin / V - 1)
    except ZeroDivisionError:
        return None, 'C'

    try:
        logrt = math.log(rt)
    except ValueError:
        return None, 'C'

    temp = 1 / (A + (B * logrt) + (C * logrt * logrt * logrt))
    tempC = temp - 273.15
    return round(tempC, 2), 'C'


def calculation_nc(value):
    A = 0.00088570897
    B = 0.00025163902
    C = 0.00000019289731

    Vin = 5.0  # v
    R = 23000.0 # 23k ohm

    # The Wagman firmware right-shifts the value by 5 bits
    V = value / 1024.0 * 5.0

    try:
        rt = R * (Vin / V - 1)
    except ZeroDivisionError:
        return None, 'C'

    try:
        logrt = math.log(rt)
    except ValueError:
        return None, 'C'

    temp = 1 / (A + B * logrt + C * logrt**3)
    tempC = temp - 273.15
    return round(tempC, 2), 'C'


conversions = [
    ('wagman_temperature_ncheatsink', calculation_nc),
    ('wagman_temperature_epheatsink', calculation_others),
    ('wagman_temperature_battery', calculation_others),
    ('wagman_temperature_brainplate', calculation_others),
    ('wagman_temperature_powersupply', calculation_others),
]
