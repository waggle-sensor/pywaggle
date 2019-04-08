# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
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
    checksum = struct.unpack_from('<H', data, offset=48)[0]

    if (sum(bincounts) & 0xFFFF) != checksum:
        values = {
            'alphasense_bins': (None, 'counts'),
            'alphasense_mtof': (None, 'us'),
            'alphasense_sample_flow_rate': (None, 'ml/s'),
            'alphasense_sampling_period': (None, 's'),
            'alphasense_pm1': (None, 'ug/m3'),
            'alphasense_pm2.5': (None, 'ug/m3'),
            'alphasense_pm10': (None, 'ug/m3'),
        }

        return values

    mtof = tuple([x / 3 for x in struct.unpack_from('<4B', data, offset=32)])
    sample_flow_rate = struct.unpack_from('<f', data, offset=36)[0]
    sampling_period = struct.unpack_from('<f', data, offset=44)[0]
    pmvalues = sorted(list(struct.unpack_from('<3f', data, offset=50)))

    values = {
        'alphasense_bins': (bincounts, 'counts'),
        'alphasense_mtof': (mtof, 'us'),
        'alphasense_sample_flow_rate': (sample_flow_rate, 'ml/s'),
        'alphasense_sampling_period': (sampling_period, 's'),
        'alphasense_pm1': (round(pmvalues[0], 3), 'ug/m3'),
        'alphasense_pm2.5': (round(pmvalues[1], 3), 'ug/m3'),
        'alphasense_pm10': (round(pmvalues[2], 3), 'ug/m3'),
    }

    return values
