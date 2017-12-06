# Conversion for alpha sensor configuration

import struct

config_data_structs = [
    ('bin boundaries', '<16H'),
    ('bin particle volume', '<16f'),
    ('bin particle density', '<16f'),
    ('bin particle weighting', '<16f'),
    ('gain scaling coefficient', '<f'),
    ('sample flow rate', '<f'),
    ('laser dac', '<B'),
    ('fan dac', '<B'),
    ('tof to sfr factor', '<B'),
]

def convert(value):
    raw_c = value['alpha_config']
    return unpack_structs(config_data_structs, raw_c)

def unpack_structs(structs, data):
    results = {}

    offset = 0

    for key, fmt in structs:
        values = struct.unpack_from(fmt, data, offset)

        if len(values) == 1:
            results[key] = (values[0], 'No unit')
        else:
            results[key] = (values, 'No unit')
        offset += struct.calcsize(fmt)

    return results