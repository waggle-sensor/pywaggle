# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import struct

content_fields = [
    ('d3s_component_id', 'B'),
    ('d3s_report_id', 'B'),

    ('d3s_status', 'I'),

    ('d3s_real_time_ms', 'I'),
    ('d3s_real_time_offset_ms', 'I'),

    ('d3s_dose', 'f'),
    ('d3s_dose_rate', 'f'),
    ('d3s_dose_user_accum', 'f'),

    ('d3s_neutron_live_time', 'I'),
    ('d3s_neutron_count', 'I'),
    ('d3s_neutron_temperature', 'h'),
    ('d3s_neutron_reserved', 'f'),

    ('d3s_gamma_live_time', 'I'),
    ('d3s_gamma_count', 'I'),
    ('d3s_gamma_temperature', 'h'),
    ('d3s_gamma_reserved', 'f'),

    ('d3s_spectrum_bit_size', 'B'),
    ('d3s_spectrum_reserved', 'B'),
]

content_names = [name for name, _ in content_fields]
content_struct = struct.Struct('<' + ''.join(type for _, type in content_fields))

def convert(value):
    content_data = value['d3s_content']
    content = content_struct.unpack(content_data)

    results = {}

    for name, val in zip(content_names, content):
        results[name] = (val, '')

    return results
