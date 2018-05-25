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


def raw_only(x):
    return x, None


def hrf_only(x):
    return None, x


def raw_and_hrf(x):
    return x, x


def coresense_mul_1000(x):
    return x, 1000 * x


def chemsense_div_100(x):
    return x, x / 100.0


def bmp180_pressure(x):
    return 100 * x, x / 100.0


def hih4030_humidity(x):
   return x, (x/1024.0*5.0)*30.68+0.958


topic_table = {
    'Coresense ID': {
        'mac_address': ('metsense', 'metsense', 'id', raw_and_hrf),
    },
    'TMP112': {
        'temperature': ('metsense', 'tmp112', 'temperature', hrf_only),
    },
    'HTU21D': {
        'temperature': ('metsense', 'htu21d', 'temperature', hrf_only),
        'humidity': ('metsense', 'htu21d', 'humidity', hrf_only),
    },
    'HIH4030': {
        'humidity': ('metsense', 'hih4030', 'humidity', hih4030_humidity),
    },
    'BMP180': {
        'temperature': ('metsense', 'bmp180', 'temperature', hrf_only),
        'pressure': ('metsense', 'bmp180', 'pressure', bmp180_pressure),
    },
    'PR103J2': {
        'temperature': ('metsense', 'pr103j2', 'temperature', raw_only),
    },
    'TSL250RD-AS': {
        'intensity': ('metsense', 'tsl250rd', 'intensity', raw_only),
    },
    'MMA8452Q': {
        'acceleration_x': ('metsense', 'mma8452q', 'acceleration_x', coresense_mul_1000),
        'acceleration_y': ('metsense', 'mma8452q', 'acceleration_y', coresense_mul_1000),
        'acceleration_z': ('metsense', 'mma8452q', 'acceleration_z', coresense_mul_1000),
    },
    'SPV1840LR5H-B': {
        'intensity': ('metsense', 'spv1840lr5h_b', 'intensity', raw_only),
    },
    'TSYS01': {
        'temperature': ('metsense', 'tsys01', 'temperature', hrf_only),
    },
    'HMC5883L': {
        'magnetic_field_x': ('lightsense', 'HMC5883L', 'magnetic_field_x', coresense_mul_1000),
        'magnetic_field_y': ('lightsense', 'HMC5883L', 'magnetic_field_y', coresense_mul_1000),
        'magnetic_field_z': ('lightsense', 'HMC5883L', 'magnetic_field_z', coresense_mul_1000),
    },
    'HIH6130': {
        'humidity': ('lightsense', 'hih6130', 'humidity', hrf_only),
        'temperature': ('lightsense', 'hih6130', 'temperature', hrf_only),
    },
    'APDS-9006-020': {
        'intensity': ('lightsense', 'apds_9006_020', 'intensity', raw_only),
    },
    'TSL260RD': {
        'intensity': ('lightsense', 'tsl260rd', 'intensity', raw_only),
    },
    'TSL250RD-LS': {
        'intensity': ('lightsense', 'tsl250rd', 'intensity', raw_only),
    },
    'MLX75305': {
        'intensity': ('lightsense', 'mlx75305', 'intensity', raw_only),
    },
    'ML8511': {
        'intensity': ('lightsense', 'ml8511', 'intensity', raw_only),
    },
    'TMP421': {
        'temperature': ('lightsense', 'tmp421', 'temperature', hrf_only),
    },
    'MLX90614': {
        'temperature': ('lightsense', 'mlx90614', 'temperature', hrf_only),
    },
    'BMI160': {
        'acceleration_x': ('chemsense', 'bmi160', 'acceleration_x', raw_only),
        'acceleration_y': ('chemsense', 'bmi160', 'acceleration_y', raw_only),
        'acceleration_z': ('chemsense', 'bmi160', 'acceleration_z', raw_only),
        'orientation_x': ('chemsense', 'bmi160', 'orientation_x', raw_only),
        'orientation_y': ('chemsense', 'bmi160', 'orientation_y', raw_only),
        'orientation_z': ('chemsense', 'bmi160', 'orientation_z', raw_only),
    },
    'Chemsense ID': {
        'mac_address': ('chemsense', 'chemsense', 'id', raw_and_hrf),
    },
    'Chemsense': {
        'co': ('chemsense', 'co', 'concentration', raw_only),
        'h2s': ('chemsense', 'h2s', 'concentration', raw_only),
        'no2': ('chemsense', 'no2', 'concentration', raw_only),
        'o3': ('chemsense', 'o3', 'concentration', raw_only),
        'so2': ('chemsense', 'so2', 'concentration', raw_only),
        'oxidizing_gases': ('chemsense', 'oxidizing_gases', 'concentration', raw_only),
        'reducing_gases': ('chemsense', 'reducing_gases', 'concentration', raw_only),
    },
    'CO ADC Temp': {
        'adc_temperature': ('chemsense', 'at0', 'temperature', chemsense_div_100),
    },
    'IAQ/IRR Temp': {
        'adc_temperature': ('chemsense', 'at1', 'temperature', chemsense_div_100),
    },
    'O3/NO2 Temp': {
        'adc_temperature': ('chemsense', 'at2', 'temperature', chemsense_div_100),
    },
    'SO2/H2S Temp': {
        'adc_temperature': ('chemsense', 'at3', 'temperature', chemsense_div_100),
    },
    'SHT25': {
        'temperature': ('chemsense', 'sht25', 'temperature', chemsense_div_100),
        'humidity': ('chemsense', 'sht25', 'humidity', chemsense_div_100),
    },
    'LPS25H': {
        'temperature': ('chemsense', 'lps25h', 'temperature', chemsense_div_100),
        'pressure': ('chemsense', 'lps25h', 'pressure', chemsense_div_100),
    },
    'Si1145': {
        'ir_intensity': ('chemsense', 'si1145', 'ir_intensity', raw_only),
        'uv_intensity': ('chemsense', 'si1145', 'uv_intensity', raw_only),
        'visible_light_intensity': ('chemsense', 'si1145', 'visible_light_intensity', raw_only),
    },
    'Rain Gauge': {
        'tip_count': ('metsense', 'rain_gauge', 'tip_count', hrf_only),
    },
    'Soil Moisture': {
        'dielectric': ('metsense', 'soil_moisture', 'dielectric', hrf_only),
        'conductivity': ('metsense', 'soil_moisture', 'conductivity', hrf_only),
        'temperature': ('metsense', 'soil_moisture', 'temperature', hrf_only),
    },
}


def make_sample(pattern, value):
    subsystem, sensor, parameter, conversion = pattern
    raw_value, hrf_value = conversion(value)
    return Sample(0, subsystem, sensor, 0, parameter, raw_value, hrf_value)


def expand_topics(readings):
    output = []

    for sensor, parameters in readings.items():
        try:
            sensor_topic_table = topic_table[sensor]
        except KeyError:
            continue

        for parameter, value in parameters.items():
            try:
                pattern = sensor_topic_table[parameter]
            except KeyError:
                continue

            output.append(make_sample(pattern, value))

    return output
