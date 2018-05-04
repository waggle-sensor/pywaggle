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
    'APDS-9006-020': {
        'intensity': ('metsense', 'apds_9006_020', 'intensity', 'raw'),
    },
    'BMI160': {
        'acceleration.x': ('metsense', 'bmi160', 'acceleration_x', 'raw'),
        'acceleration.y': ('metsense', 'bmi160', 'acceleration_y', 'raw'),
        'acceleration.z': ('metsense', 'bmi160', 'acceleration_z', 'raw'),
        'orientation.x': ('metsense', 'bmi160', 'orientation_x', 'raw'),
        'orientation.y': ('metsense', 'bmi160', 'orientation_y', 'raw'),
        'orientation.z': ('metsense', 'bmi160', 'orientation_z', 'raw'),
    },
    'BMP180': {
        'pressure': ('metsense', 'bmp180', 'pressure', 'hrf'),
        'temperature': ('metsense', 'bmp180', 'temperature', 'hrf'),
    },
    'Chemsense': {
        'co': ('chemsense', 'co', 'concentration', 'raw'),
        'h2s': ('chemsense', 'h2s', 'concentration', 'raw'),
        'no2': ('chemsense', 'no2', 'concentration', 'raw'),
        'o3': ('chemsense', 'o3', 'concentration', 'raw'),
        'so2': ('chemsense', 'so2', 'concentration', 'raw'),
        'oxidizing_gases': ('chemsense', 'oxidizing_gases', 'concentration', 'raw'),
        'reducing_gases': ('chemsense', 'reducing_gases', 'concentration', 'raw'),
    },
    'HIH4030': {
        'humidity': ('lightsense', 'hih4030', 'humidity', 'raw'),
    },
    'HIH6130': {
        'humidity': ('lightsense', 'hih4030', 'humidity', 'hrf'),
        'temperature': ('lightsense', 'hih4030', 'temperature', 'hrf'),
    },
    'HTU21D': {
        'temperature': ('metsense', 'htu21d', 'temperature', 'hrf'),
        'humidity': ('metsense', 'htu21d', 'humidity', 'hrf'),
    },
    'BMP180': {
        'temperature': ('metsense', 'bmp180', 'temperature', 'hrf'),
        'pressure': ('metsense', 'bmp180', 'pressure', 'raw'),
    },
    'MMA8452Q': {
        'acceleration.x': ('metsense', 'mma8452q', 'acceleration_x', 'hrf'),
        'acceleration.y': ('metsense', 'mma8452q', 'acceleration_y', 'hrf'),
        'acceleration.z': ('metsense', 'mma8452q', 'acceleration_z', 'hrf'),
    },
    'TSL250RD-AS': {
        'intensity': ('metsense', 'tsl250rd', 'intensity', 'raw'),
    },
    'TSL250RD-LS': {
        'intensity': ('lightsense', 'tsl250rd', 'intensity', 'raw'),
    },
    'TSL260RD': {
        'intensity': ('metsense', 'tsl260rd', 'intensity', 'raw'),
    },
    'TSYS01': {
        'temperature': ('lightsense', 'tsys01', 'temperature', 'hrf'),
    },
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
