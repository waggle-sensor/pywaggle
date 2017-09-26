# Conversion for HTU21D temperature

# temperature = -46.85 + 175.72 * raw_value / 2^16

def convert(value):
    # get rid of status bits
    value &= 0xFFFC

    t = value / float(pow(2, 16))
    temperature = -46.85 + (175.72 * t)
    return round(temperature, 2), 'C'
