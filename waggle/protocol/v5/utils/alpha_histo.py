# Conversion for alpha histogram data

import struct

histogram_data_structs = [
    ('bins', '<16H'),
    ('mtof', '<4B'),
    ('sample flow rate', '<f'),
    ('weather', '<f'),
    ('sampling period', '<f'),
    ('checksum', '<H'),
    ('pm1', '<f'),
    ('pm2.5', '<f'),
    ('pm10', '<f'),
]

def convert(value):
    raw_h = value['alpha_histo']
    return decode(raw_h)


def decode(data):
    bincounts = struct.unpack_from('<16H', data, offset=0)
    mtof = [x / 3 for x in struct.unpack_from('<4B', data, offset=32)]
    sample_flow_rate = struct.unpack_from('<f', data, offset=36)[0]
    pressure = struct.unpack_from('<f', data, offset=40)[0]
    temperature = pressure / 10.0
    sampling_period = struct.unpack_from('<f', data, offset=44)[0]
    checksum = struct.unpack_from('<H', data, offset=48)[0]
    pmvalues = sorted(list(struct.unpack_from('<3f', data, offset=50)))

    values = {
        'bins': (bincounts, 'counts'),
        'mtof': (mtof, 'us'),
        'sample flow rate': (sample_flow_rate, 'ml/s'),
        'sampling period': (sampling_period, 's'),
        'pm1': (pmvalues[0], 'ug/m3'),
        'pm2.5': (pmvalues[1], 'ug/m3'),
        'pm10': (pmvalues[2], 'ug/m3'),
    }

    # if temperature > 200:
    #     values['pressure'] = (pressure, 'Pa')
    # else:
    #     values['temperature'] = (temperature, 'C')

    return values
