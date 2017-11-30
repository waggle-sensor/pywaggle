# Conversion for bus readings

bus_type = {
    0: 'i2c',
    1: 'spi',
    2: 'serial',
    3: 'analog',
    4: 'digital',
    5: 'pwm'
}

def convert(value):
    raw_s = value['bus_reading']

    value = {}
    idx = 0
    while (len(raw_s) > 0):
        val = 0
        data_length = (raw_s[0] & 0x7F) - 2
        b_type = raw_s[1]
        b_address = raw_s[2]
        data = raw_s[3:data_length + 3]
        raw_s = raw_s[data_length + 3::]

        if b_type != 2:
            for i in range(len(data)):
                val = (val << 8) | data[i]
        else:
            val = data

        key = 'bus' + str(idx)
        value[key] = {}
        value[key]['bus_type'] = bus_type[b_type]
        value[key]['bus_address'] = b_address
        value[key]['bus_reading'] = val

        idx += 1

    return value