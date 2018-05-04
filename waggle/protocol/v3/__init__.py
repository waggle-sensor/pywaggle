from waggle.coresense.utils import decode_frame
from collections import namedtuple

Sample = namedtuple('Sample', [
    'timestamp',
    'subsystem',
    'sensor',
    'instance',
    'parameter',
    'value_raw',
    'value_hrf',
])

waggle_protocol_version='0.3'


def unpack_sensors(packet):
    return expand_topics(decode_frame(packet))


# TODO complete from table
topic_table = {
    'HTU21D': {
        'temperature': ('metsense', 'htu21d', 'temperature', 'hrf'),
        'humidity': ('metsense', 'htu21d', 'humidity', 'hrf'),
    },
    'HIH4030': {
        'humidity': ('lightsense', 'hih4030', 'humidity', 'raw'),
    },
    'BMP180': {
        'temperature': ('metsense', 'bmp180', 'temperature', 'hrf'),
        'pressure': ('metsense', 'bmp180', 'pressure', 'raw'),
    },
    'MMA8452Q': {
        'acceleration.x': ('metsense', 'mma8452q', 'acceleration_x', 'hrf'),
        'acceleration.y': ('metsense', 'mma8452q', 'acceleration_y', 'hrf'),
        'acceleration.z': ('metsense', 'mma8452q', 'acceleration_z', 'hrf'),
    }
}


def make_sample(pattern, value):
    subsystem, sensor, parameter, type = pattern
    if type == 'raw':
        return Sample(0, subsystem, sensor, 0, parameter, value, None)
    if type == 'hrf':
        return Sample(0, subsystem, sensor, 0, parameter, None, value)
    raise ValueError('No value type {}'.format(type))


def expand_topics(readings):
    output = []

    for sensor, parameters in readings.items():
        for parameter, value in parameters.items():
            try:
                pattern = topic_table[sensor][parameter]
            except KeyError:
                continue
            output.append(make_sample(pattern, value))

    return output
