# Conversion for HTU21D humidity

# temperature = -6 + 125 * raw_value / 2^16

def convert(value):
    # get rid of status bits
    value &= 0xFFFC

    h = value / float(pow(2, 16))
    humidity = -6.0 + (125.0 * h)
    return round(humidity, 2), '%RH'
