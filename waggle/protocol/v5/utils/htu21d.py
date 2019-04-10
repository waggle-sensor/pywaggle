# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for HTU21D temperature
# temperature = -46.85 + 175.72 * raw_value / 2^16

# Conversion for HTU21D humidity
# humidity = -6 + 125 * raw_value / 2^16

def convert_using(value, key_t, key_h):
    raw_t = value[key_t]
    raw_h = value[key_h]

    raw_t &= 0xFFFC
    raw_h &= 0xFFFC

    # temperature
    # get rid of status bits
    t = raw_t / 2**16
    temperature = -46.85 + (175.72 * t)

    # humidity
    # get rid of status bits

    h = raw_h / 2**16
    humidity = -6.0 + (125.0 * h)

    temperature_rounded = round(temperature, 2)
    humidity_rounded = round(humidity, 2)

    value[key_t] = (temperature_rounded, 'C')
    value[key_h] = (humidity_rounded, '%RH')


def convert(value):
    for key_t, key_h in conversions:
        try:
            convert_using(value, key_t, key_h)
        except KeyError:
            pass

    try:
        t = value['wagman_htu21d_temperature']
        h = value['wagman_htu21d_humidity']

        t_rounded = round(t, 2)
        h_rounded = round(h, 2)

        value['wagman_htu21d_temperature'] = (t_rounded, 'C')
        value['wagman_htu21d_humidity'] = (h_rounded, '%RH')
    except KeyError:
        pass

    return value


conversions = [
    ('metsense_htu21d_temperature', 'metsense_htu21d_humidity'),
    # ('wagman_htu21d_temperature', 'wagman_htu21d_humidity'),
]
