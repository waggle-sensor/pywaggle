# Conversion for HTU21D temperature
# temperature = -46.85 + 175.72 * raw_value / 2^16

# Conversion for HTU21D humidity
# humidity = -6 + 125 * raw_value / 2^16

def convert(value):
    raw_t = value[0x02]['metsense_htu21d_temperature']
    raw_h = value[0x02]['metsense_htu21d_humidity']

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



    return round(temperature, 2), 'C', round(humidity, 2), '%RH'
