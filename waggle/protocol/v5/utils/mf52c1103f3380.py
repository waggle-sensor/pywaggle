# Conversion to temperature in degree Celsius

# Coefficients for MF12 10k 3380 thermistor in -30 C to 110 C
# referred to http://www.cantherm.com/choosing_ntc
# T = 1 / (A + (B * ln(rt)) + (C *ln(rt)^3)), in Kelvin

# This conversion is tested in Wagman hw V3.1 ker v1.0.4

import math

def convert(value):
    raw = []
    raw_ncheatsink = value['wagman_temperature_ncheatsink']
    raw.append(value['wagman_temperature_epheatsink'])
    raw.append(value['wagman_temperature_battery'])
    raw.append(value['wagman_temperature_brainplate'])
    raw.append(value['wagman_temperature_powersupply'])

    assert isinstance(value, int)

    #/*** for wagman_temperature_ncheatsink ***/
    v_in = 5.0  # v
    R = 23000.0 # 23k ohm

    v = raw_ncheatsink / 1024.0 * 5.0
    value['wagman_temperature_ncheatsink'] = []
    value['wagman_temperature_ncheatsink'].extend((calculation(v_in, v, R), 'C'))


    # for other temperature    
    v_in = 1.8  # v
    R = 23000.0 # 23k ohm
    LSB = 0.0000625 # 6.25 uV for 16-bit ADC converter

    # The Wagman firmware right-shifts the value by 5 bits
    for i in range(len(raw)):
        raw[i] = raw[i] << 5
        v = raw[i] * LSB
        calculation(v_in, v, R)

    value['wagman_temperature_epheatsink'] = []
    value['wagman_temperature_epheatsink'].extend((raw[0], 'C'))
    value['wagman_temperature_battery'] = []
    value['wagman_temperature_battery'].extend((raw[1], 'C'))
    value['wagman_temperature_brainplate'] = []
    value['wagman_temperature_brainplate'].extend((raw[2], 'C'))
    value['wagman_temperature_powersupply'] = []
    value['wagman_temperature_powersupply'].extend((raw[3], 'C'))

    return value

def calculation(vin, vcal, r):
    A = 0.00088570897
    B = 0.00025163902
    C = 0.00000019289731

    rt = R * (v_in / v - 1)
    logrt = math.log(rt)
    temp = 1 / (A + (B * logrt) + (C * logrt * logrt * logrt))
    tempC_ncheatsink = temp - 273.15
