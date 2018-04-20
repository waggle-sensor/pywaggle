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
    t = raw_t / float(pow(2, 16))
    temperature = -46.85 + (175.72 * t)

    # humidity
    # get rid of status bits

    h = raw_h / float(pow(2, 16))
    humidity = -6.0 + (125.0 * h)

    value[key_t] = (round(temperature, 2), 'C')
    value[key_h] = (round(humidity, 2), '%RH')


def convert(value):
    for key_t, key_h in conversions:
        try:
            convert_using(value, key_t, key_h)
        except KeyError:
            pass

    return value


conversions = [
    ('metsense_htu21d_temperature', 'metsense_htu21d_humidity'),
    ('wagman_htu21d_temperature', 'wagman_htu21d_humidity'),
]
