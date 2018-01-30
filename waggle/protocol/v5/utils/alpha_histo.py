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
    mtof = tuple([x / 3 for x in struct.unpack_from('<4B', data, offset=32)])
    sample_flow_rate = struct.unpack_from('<f', data, offset=36)[0]
    sampling_period = struct.unpack_from('<f', data, offset=44)[0]
    pmvalues = sorted(list(struct.unpack_from('<3f', data, offset=50)))

    values = {
        'alphasense_bins': (bincounts, 'counts'),
        'alphasense_mtof': (mtof, 'us'),
        'alphasense_sample_flow_rate': (sample_flow_rate, 'ml/s'),
        'alphasense_sampling_period': (sampling_period, 's'),
        'alphasense_pm1': (pmvalues[0], 'ug/m3'),
        'alphasense_pm2.5': (pmvalues[1], 'ug/m3'),
        'alphasense_pm10': (pmvalues[2], 'ug/m3'),
    }

    return values
