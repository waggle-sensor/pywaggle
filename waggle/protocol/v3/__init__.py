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
    'Coresense ID': {
        'mac_address': ('metsense', 'metsense', 'id', 'both'),
    },
    'TMP112': {
        'temperature': ('metsense', 'tmp112', 'temperature', 'hrf'),
    },
    'HTU21D': {
        'temperature': ('metsense', 'htu21d', 'temperature', 'hrf'),
        'humidity': ('metsense', 'htu21d', 'humidity', 'hrf'),
    },
    'HIH4030': {
        'humidity': ('metsense', 'hih4030', 'humidity', 'raw'),
    },
    'BMP180': {
        'temperature': ('metsense', 'bmp180', 'temperature', 'hrf'),
        'pressure': ('metsense', 'bmp180', 'pressure', 'hrf'),
    },
    'PR103J2': {
        'temperature': ('metsense', 'pr103j2', 'temperature', 'raw'),
    },
    'TSL250RD-AS': {
        'intensity': ('metsense', 'tsl250rd', 'intensity', 'raw'),
    },
    'MMA8452Q': {
        'acceleration_x': ('metsense', 'mma8452q', 'acceleration_x', 'hrf'),
        'acceleration_y': ('metsense', 'mma8452q', 'acceleration_y', 'hrf'),
        'acceleration_z': ('metsense', 'mma8452q', 'acceleration_z', 'hrf'),
    },
    'SPV1840LR5H-B': {
        'intensity': ('metsense', 'spv1840lr5h_b', 'intensity', 'raw'),
    },
    'TSYS01': {
        'temperature': ('lightsense', 'tsys01', 'temperature', 'hrf'),
    },
    'HMC5883L': {
        'magnetic_field_x': ('metsense', 'HMC5883L', 'hx', 'hrf'),
        'magnetic_field_y': ('metsense', 'HMC5883L', 'hy', 'hrf'),
        'magnetic_field_z': ('metsense', 'HMC5883L', 'hz', 'hrf'),
    },
    'HIH6130': {
        'humidity': ('lightsense', 'hih4030', 'humidity', 'hrf'),
        'temperature': ('lightsense', 'hih4030', 'temperature', 'hrf'),
    },
    'APDS-9006-020': {
        'intensity': ('metsense', 'apds_9006_020', 'intensity', 'raw'),
    },
    'TSL260RD': {
        'intensity': ('metsense', 'tsl260rd', 'intensity', 'raw'),
    },
    'TSL250RD-LS': {
        'intensity': ('lightsense', 'tsl250rd', 'intensity', 'raw'),
    },
    'MLX75305': {
        'intensity': ('lightsense', 'mlx75305', 'intensity', 'raw'),
    },
    'ML8511': {
        'intensity': ('lightsense', 'ml8511', 'intensity', 'raw'),
    },
    'BMI160': {
        'acceleration_x': ('metsense', 'bmi160', 'acceleration_x', 'raw'),
        'acceleration_y': ('metsense', 'bmi160', 'acceleration_y', 'raw'),
        'acceleration_z': ('metsense', 'bmi160', 'acceleration_z', 'raw'),
        'orientation_x': ('metsense', 'bmi160', 'orientation_x', 'raw'),
        'orientation_y': ('metsense', 'bmi160', 'orientation_y', 'raw'),
        'orientation_z': ('metsense', 'bmi160', 'orientation_z', 'raw'),
    },
    'BMP180': {
        'pressure': ('metsense', 'bmp180', 'pressure', 'hrf'),
        'temperature': ('metsense', 'bmp180', 'temperature', 'hrf'),
    },
    'Chemsense': {
        'mac_address': ('chemsense', 'chemsense', 'id', 'both'),
        'co': ('chemsense', 'co', 'concentration', 'raw'),
        'h2s': ('chemsense', 'h2s', 'concentration', 'raw'),
        'no2': ('chemsense', 'no2', 'concentration', 'raw'),
        'o3': ('chemsense', 'o3', 'concentration', 'raw'),
        'so2': ('chemsense', 'so2', 'concentration', 'raw'),
        'oxidizing_gases': ('chemsense', 'oxidizing_gases', 'concentration', 'raw'),
        'reducing_gases': ('chemsense', 'reducing_gases', 'concentration', 'raw'),
    },
    'SHT25': {
        'temperature': ('chemsense', 'sht25', 'temperature', 'raw'),
        'humidity': ('chemsense', 'sht25', 'humidity', 'raw'),
    },
    'LPS25H': {
        'temperature': ('chemsense', 'lps25h', 'temperature', 'raw'),
        'pressure': ('chemsense', 'lps25h', 'pressure', 'raw'),
    },
    'Si1145': {
        'ir_intensity': ('chemsense', 'si1145', 'ir_intensity', 'raw'),
        'uv_intensity': ('chemsense', 'si1145', 'uv_intensity', 'raw'),
        'visible_light_intensity': ('chemsense', 'si1145', 'visible_light_intensity', 'raw'),
    }
}


def make_sample(pattern, value):
    subsystem, sensor, parameter, type = pattern
    if type == 'raw':
        return Sample(0, subsystem, sensor, 0, parameter, value, None)
    if type == 'hrf':
        return Sample(0, subsystem, sensor, 0, parameter, None, value)
    if type == 'both':
        return Sample(0, subsystem, sensor, 0, parameter, value, value)
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
