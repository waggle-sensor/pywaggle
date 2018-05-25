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


def div_100(x):
    return x/100.0


def mul_1000(x):
    return 1000*x


topic_table = {
    'Coresense ID': {
        'mac_address': ('metsense', 'metsense', 'id', 'both', None),
    },
    'TMP112': {
        'temperature': ('metsense', 'tmp112', 'temperature', 'hrf', None),
    },
    'HTU21D': {
        'temperature': ('metsense', 'htu21d', 'temperature', 'hrf', None),
        'humidity': ('metsense', 'htu21d', 'humidity', 'hrf', None),
    },
    'HIH4030': {
        'humidity': ('metsense', 'hih4030', 'humidity', 'raw', None),
    },
    'BMP180': {
        'temperature': ('metsense', 'bmp180', 'temperature', 'hrf', None),
        'pressure': ('metsense', 'bmp180', 'pressure', 'hrf', div_100),
    },
    'PR103J2': {
        'temperature': ('metsense', 'pr103j2', 'temperature', 'raw', None),
    },
    'TSL250RD-AS': {
        'intensity': ('metsense', 'tsl250rd', 'intensity', 'raw', None),
    },
    'MMA8452Q': {
        'acceleration_x': ('metsense', 'mma8452q', 'acceleration_x', 'hrf', mul_1000),
        'acceleration_y': ('metsense', 'mma8452q', 'acceleration_y', 'hrf', mul_1000),
        'acceleration_z': ('metsense', 'mma8452q', 'acceleration_z', 'hrf', mul_1000),
    },
    'SPV1840LR5H-B': {
        'intensity': ('metsense', 'spv1840lr5h_b', 'intensity', 'raw', None),
    },
    'TSYS01': {
        'temperature': ('metsense', 'tsys01', 'temperature', 'hrf', None),
    },
    'HMC5883L': {
        'magnetic_field_x': ('lightsense', 'HMC5883L', 'magnetic_field_x', 'hrf', mul_1000),
        'magnetic_field_y': ('lightsense', 'HMC5883L', 'magnetic_field_y', 'hrf', mul_1000),
        'magnetic_field_z': ('lightsense', 'HMC5883L', 'magnetic_field_z', 'hrf', mul_1000),
    },
    'HIH6130': {
        'humidity': ('lightsense', 'hih6130', 'humidity', 'hrf', None),
        'temperature': ('lightsense', 'hih6130', 'temperature', 'hrf', None),
    },
    'APDS-9006-020': {
        'intensity': ('lightsense', 'apds_9006_020', 'intensity', 'raw', None),
    },
    'TSL260RD': {
        'intensity': ('lightsense', 'tsl260rd', 'intensity', 'raw', None),
    },
    'TSL250RD-LS': {
        'intensity': ('lightsense', 'tsl250rd', 'intensity', 'raw', None),
    },
    'MLX75305': {
        'intensity': ('lightsense', 'mlx75305', 'intensity', 'raw', None),
    },
    'ML8511': {
        'intensity': ('lightsense', 'ml8511', 'intensity', 'raw', None),
    },
    'TMP421': {
        'temperature': ('lightsense', 'tmp421', 'temperature', 'hrf', None),
    },
    'MLX90614': {
        'temperature': ('lightsense', 'mlx90614', 'temperature', 'hrf', None),
    },
    'BMI160': {
        'acceleration_x': ('chemsense', 'bmi160', 'acceleration_x', 'raw', None),
        'acceleration_y': ('chemsense', 'bmi160', 'acceleration_y', 'raw', None),
        'acceleration_z': ('chemsense', 'bmi160', 'acceleration_z', 'raw', None),
        'orientation_x': ('chemsense', 'bmi160', 'orientation_x', 'raw', None),
        'orientation_y': ('chemsense', 'bmi160', 'orientation_y', 'raw', None),
        'orientation_z': ('chemsense', 'bmi160', 'orientation_z', 'raw', None),
    },
    'Chemsense': {
        'mac_address': ('chemsense', 'chemsense', 'id', 'both', None),
        'co': ('chemsense', 'co', 'concentration', 'raw', None),
        'h2s': ('chemsense', 'h2s', 'concentration', 'raw', None),
        'no2': ('chemsense', 'no2', 'concentration', 'raw', None),
        'o3': ('chemsense', 'o3', 'concentration', 'raw', None),
        'so2': ('chemsense', 'so2', 'concentration', 'raw', None),
        'oxidizing_gases': ('chemsense', 'oxidizing_gases', 'concentration', 'raw', None),
        'reducing_gases': ('chemsense', 'reducing_gases', 'concentration', 'raw', None),
    },
    'CO ADC Temp': {
        'adc_temperature': ('chemsense', 'at0', 'temperature', 'raw', div_100),
    },
    'IAQ/IRR Temp': {
        'adc_temperature': ('chemsense', 'at1', 'temperature', 'raw', div_100),
    },
    'O3/NO2 Temp': {
        'adc_temperature': ('chemsense', 'at2', 'temperature', 'raw', div_100),
    },
    'SO2/H2S Temp': {
        'adc_temperature': ('chemsense', 'at3', 'temperature', 'raw', div_100),
    },
    'SHT25': {
        'temperature': ('chemsense', 'sht25', 'temperature', 'raw', div_100),
        'humidity': ('chemsense', 'sht25', 'humidity', 'raw', div_100),
    },
    'LPS25H': {
        'temperature': ('chemsense', 'lps25h', 'temperature', 'raw', div_100),
        'pressure': ('chemsense', 'lps25h', 'pressure', 'raw', div_100),
    },
    'Si1145': {
        'ir_intensity': ('chemsense', 'si1145', 'ir_intensity', 'raw', None),
        'uv_intensity': ('chemsense', 'si1145', 'uv_intensity', 'raw', None),
        'visible_light_intensity': ('chemsense', 'si1145', 'visible_light_intensity', 'raw', None),
    },
    'Rain Gauge': {
        'tip_count': ('metsense', 'rain_gauge', 'tip_count', 'hrf', None),
    },
    'Soil Moisture': {
        'dielectric': ('metsense', 'soil_moisture', 'dielectric', 'hrf', None),
        'conductivity': ('metsense', 'soil_moisture', 'conductivity', 'hrf', None),
        'temperature': ('metsense', 'soil_moisture', 'temperature', 'hrf', None),
    },
}


def make_sample(pattern, value):
    subsystem, sensor, parameter, type, conversion = pattern

    if type == 'raw':
        raw_value = value
        hrf_value = None
    elif type == 'hrf':
        raw_value = None
        hrf_value = value
    elif type == 'both':
        raw_value = value
        hrf_value = value
    else:
        raise ValueError('No value type {}'.format(type))

    # assuming value is correct type for conversion, otherwise we'd have all
    # required values and no need for conversion.
    if conversion is not None:
        hrf_value = conversion(value)

    return Sample(0, subsystem, sensor, 0, parameter, raw_value, hrf_value)


def expand_topics(readings):
    output = []

    for sensor, parameters in readings.items():
        sensor_topic_table = topic_table[sensor]
        for parameter, value in parameters.items():
            try:
                pattern = sensor_topic_table[parameter]
            except KeyError:
                continue
            output.append(make_sample(pattern, value))

    return output
