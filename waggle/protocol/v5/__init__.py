# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from .decoder import decode_frame
from .decoder import convert
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

waggle_protocol_version='0.5'

drop_raw = [
    'metsense_spv1840lr5h-b',
    'image_histogram_r',
    'image_histogram_g',
    'image_histogram_b',
]


def unpack_result(results, key, value, unit):
    if key not in results:
        results[key] = {}

    if unit == 'raw':
        results[key]['raw'] = value
    else:
        results[key]['hrf'] = value
        results[key]['hrf_units'] = unit


def unpack_sensors(packet):
    unpacked_data = decode_frame(packet)

    results = {}

    for sensor_id, sensor_data in unpacked_data.items():
        for key, value in sensor_data.items():
            results[key] = {'raw': value}

    for sensor_id, sensor_data in unpacked_data.items():
        try:
            for key, entry in convert(sensor_data, sensor_id).items():
                # hack in support for multiple results
                if not isinstance(entry, list):
                    entry = [entry]

                for value, unit in entry:
                    unpack_result(results, key, value, unit)
        except Exception:
            pass

    for key in drop_raw:
        try:
            del results[key]['raw']
        except KeyError:
            continue

    return [Sample(0, subsystem, sensor, 0, parameter, v.get('raw'), v.get('hrf'))
            for (subsystem, sensor, parameter), v in expand_topics(results).items()]


topics_table = {
    'metsense': {
        'bmp180': {
            'pressure': 'metsense_bmp180_pressure',
            'temperature': 'metsense_bmp180_temperature',
        },
        'hih4030': {
            'humidity': 'metsense_hih4030_humidity',
        },
        'htu21d': {
            'humidity': 'metsense_htu21d_humidity',
            'temperature': 'metsense_htu21d_temperature',
        },
        'mma8452q': {
            'acceleration_x': 'metsense_mma8452q_acc_x',
            'acceleration_y': 'metsense_mma8452q_acc_y',
            'acceleration_z': 'metsense_mma8452q_acc_z',
        },
        'pr103j2': {
            'temperature': 'metsense_pr103j2_temperature',
        },
        'spv1840lr5h_b': {
            'intensity': 'metsense_spv1840lr5h-b',
        },
        'tmp112': {
            'temperature': 'metsense_tmp112',
        },
        'tsl250rd': {
            'intensity': 'metsense_tsl250rd_light',
        },
        'tsys01': {
            'temperature': 'metsense_tsys01_temperature',
        },
        'metsense': {
            'id': 'metsense_id',
        },
        'rg3': {
            'onset_rain': 'rg3_onset_rain',
        },
        '5te': {
            'soil_dielectric': '5te_soil_dielectric',
            'soil_conductivity': '5te_soil_conductivity',
            'soil_temperature': '5te_soil_temperature',
        },
    },
    'lightsense': {
        'apds_9006_020': {
            'intensity': 'lightsense_apds_9006_020_light'
        },
        'hih6130': {
            'humidity': 'lightsense_hih6130_humidity',
            'temperature': 'lightsense_hih6130_temperature',
        },
        'hmc5883l': {
            'magnetic_field_x': 'lightsense_hmc5883l_hx',
            'magnetic_field_y': 'lightsense_hmc5883l_hy',
            'magnetic_field_z': 'lightsense_hmc5883l_hz',
        },
        'ml8511': {
            'intensity': 'lightsense_ml8511',
        },
        'mlx75305': {
            'intensity': 'lightsense_mlx75305',
        },
        'tmp421': {
            'temperature': 'lightsense_tmp421',
        },
        'tsl250rd': {
            'intensity': 'lightsense_tsl250_light',
        },
        'tsl260rd': {
            'intensity': 'lightsense_tsl260_light',
        },
    },
    'chemsense': {
        'lps25h': {
            'pressure': 'chemsense_lpp',
            'temperature': 'chemsense_lpt',
        },
        'sht25': {
            'humidity': 'chemsense_shh',
            'temperature': 'chemsense_sht',
        },
        'si1145': {
            'ir_intensity': 'chemsense_sir',
            'uv_intensity': 'chemsense_suv',
            'visible_light_intensity': 'chemsense_svl',
        },
        'chemsense': {
            'id': 'chemsense_id',
        },
        'co': {
            'concentration': 'chemsense_cmo',
        },
        'h2s': {
            'concentration': 'chemsense_h2s',
        },
        'no2': {
            'concentration': 'chemsense_no2',
        },
        'o3': {
            'concentration': 'chemsense_ozo',
        },
        'so2': {
            'concentration': 'chemsense_so2',
        },
        'reducing_gases': {
            'concentration': 'chemsense_irr',
        },
        'oxidizing_gases': {
            'concentration': 'chemsense_iaq',
        },
        'at0': {
            'temperature': 'chemsense_at0',
        },
        'at1': {
            'temperature': 'chemsense_at1',
        },
        'at2': {
            'temperature': 'chemsense_at2',
        },
        'at3': {
            'temperature': 'chemsense_at3',
        },
    },
    'alphasense': {
        'opc_n2': {
            'pm1': 'alphasense_pm1',
            'pm2_5': 'alphasense_pm2.5',
            'pm10': 'alphasense_pm10',
            'bins': 'alphasense_bins',
            'sample_flow_rate': 'alphasense_sample_flow_rate',
            'sampling_period': 'alphasense_sampling_period',
            'id': 'alpha_serial',
            'fw': 'alpha_firmware',
        }
    },
    'plantower': {
        'pms7003': {
            '10um_particle': 'pms7003_10um_particle',
            '1um_particle': 'pms7003_1um_particle',
            '2_5um_particle': 'pms7003_2_5um_particle',
            '5um_particle': 'pms7003_5um_particle',
            'pm10_atm': 'pms7003_pm10_atm',
            'pm10_cf1': 'pms7003_pm10_cf1',
            'pm1_atm': 'pms7003_pm1_atm',
            'pm1_cf1': 'pms7003_pm1_cf1',
            'pm25_atm': 'pms7003_pm25_atm',
            'pm25_cf1': 'pms7003_pm25_cf1',
            'point_3um_particle': 'pms7003_point_3um_particle',
            'point_5um_particle': 'pms7003_point_5um_particle',
        },
    },
    'nc': {
        'uptime': {
            'uptime': 'nc_uptime',
            'idletime': 'nc_idletime',
        },
        'loadavg': {
            'load_1': 'nc_load_1',
            'load_5': 'nc_load_5',
            'load_10': 'nc_load_10',
        },
        'mem': {
            'total': 'nc_ram_total',
            'free': 'nc_ram_free',
        },
        'media': {
            'current': 'nc_current_disk_type',
            'other': 'nc_alternate_disk_type',
        },
        'disk_boot': {
            'used': 'nc_partition1_used',
            'total': 'nc_partition1_total',
        },
        'disk_root': {
            'used': 'nc_partition2_used',
            'total': 'nc_partition2_total',
        },
        'disk_wagglerw': {
            'used': 'nc_partition3_used',
            'total': 'nc_partition3_total',
        },
        'net_broadband': {
            'rx': 'net_broadband_rx',
            'tx': 'net_broadband_tx',
        },
        'net_lan': {
            'rx': 'net_lan_rx',
            'tx': 'net_lan_tx',
        },
        'net_usb': {
            'rx': 'net_usb_rx',
            'tx': 'net_usb_tx',
        },
        'devices': {
            'alphasense': 'nc_devices_alphasense',
            'coresense': 'nc_devices_metsense',
            'modem': 'nc_devices_modem',
            'wagman': 'nc_devices_wagman',
        },
        'service_rabbitmq': {
            'uptime': 'nc_service_rabbitmq_uptime',
            'state': 'nc_service_rabbitmq_state',
            'substate': 'nc_service_rabbitmq_substate',
        },
    },
    'ep': {
        'uptime': {
            'uptime': 'ep_uptime',
            'idletime': 'ep_idletime',
        },
        'loadavg': {
            'load_1': 'ep_load_1',
            'load_5': 'ep_load_5',
            'load_10': 'ep_load_10',
        },
        'mem': {
            'total': 'ep_ram_total',
            'free': 'ep_ram_free',
        },
        'media': {
            'current': 'ep_current_disk_type',
            'other': 'ep_alternate_disk_type',
        },
        'disk_boot': {
            'used': 'ep_partition1_used',
            'total': 'ep_partition1_total',
        },
        'disk_root': {
            'used': 'ep_partition2_used',
            'total': 'ep_partition2_total',
        },
        'disk_wagglerw': {
            'used': 'ep_partition3_used',
            'total': 'ep_partition3_total',
        },
        'devices': {
            'bottom_camera': 'ep_devices_camera_bottom',
            'top_camera': 'ep_devices_camera_top',
            'microphone': 'ep_devices_microphone',
        },
        'service_rabbitmq': {
            'uptime': 'ep_service_rabbitmq_uptime',
            'state': 'ep_service_rabbitmq_state',
            'substate': 'ep_service_rabbitmq_substate',
        },
    },
    'wagman': {
        'wagman': {
            'id': 'wagman_id',
        },
        'hw_ver': {
            'major': 'wagman_ver_hw_mj',
            'minor': 'wagman_ver_hw_mi',
        },
        'sw_ver': {
            'major': 'wagman_ver_sw_mj',
            'minor': 'wagman_ver_sw_mi',
            'patch': 'wagman_ver_sw_p',
        },
        'git_ver': {
            'commit': 'wagman_ver_git',
        },
        'boot': {
            'flags': 'wagman_bootloader_nc_flag',
            'count': 'wagman_boot_count',
        },
        'uptime': {
            'uptime': 'wagman_uptime',
        },
        'current': {
            'wagman': 'wagman_current_wagman',
            'nc': 'wagman_current_nc',
            'ep': 'wagman_current_ep',
            'cs': 'wagman_current_cs',
        },
        'failures': {
            'nc': 'wagman_failcount_nc',
            'ep': 'wagman_failcount_ep',
            'cs': 'wagman_failcount_cs',
        },
        'temperatures': {
            'nc_heatsink': 'wagman_temperature_ncheatsink',
            'ep_heatsink': 'wagman_temperature_epheatsink',
            'battery': 'wagman_temperature_battery',
            'brainplate': 'wagman_temperature_brainplate',
            'powersupply': 'wagman_temperature_powersupply',
        },
        'enabled': {
            'nc': 'wagman_enabled_nc',
            'ep': 'wagman_enabled_ep',
            'cs': 'wagman_enabled_cs',
        },
        'heartbeat': {
            'nc': 'wagman_heartbeat_nc',
            'ep': 'wagman_heartbeat_ep',
            'cs': 'wagman_heartbeat_cs',
        },
        'media': {
            'nc': 'wagman_mediaselect_nc',
            'ep': 'wagman_mediaselect_ep',
        },
        'htu21d': {
            'temperature': 'wagman_htu21d_temperature',
            'humidity': 'wagman_htu21d_humidity',
        },
        'hih4030': {
            'humidity': 'wagman_hih4030_humidity',
        },
        'light': {
            'intensity': 'wagman_light',
        },
    },
    'image': {
        'device': {
            'device': 'image_device',
        },
        'avg': {
            'r': 'image_average_color_r',
            'g': 'image_average_color_g',
            'b': 'image_average_color_b',
        },
        'hist': {
            'r': 'image_histogram_r',
            'g': 'image_histogram_g',
            'b': 'image_histogram_b',
        }
    },
    'audio': {
        'microphone': {
            'octave_1_intensity': 'audio_spl_octave1',
            'octave_2_intensity': 'audio_spl_octave2',
            'octave_3_intensity': 'audio_spl_octave3',
            'octave_4_intensity': 'audio_spl_octave4',
            'octave_5_intensity': 'audio_spl_octave5',
            'octave_6_intensity': 'audio_spl_octave6',
            'octave_7_intensity': 'audio_spl_octave7',
            'octave_8_intensity': 'audio_spl_octave8',
            'octave_9_intensity': 'audio_spl_octave9',
            'octave_10_intensity': 'audio_spl_octave10',
            'octave_total_intensity': 'audio_spl_octave_total',
        }
    },
    'radiation': {
        'd3s': {
            'component_id': 'd3s_component_id',
            'report_id': 'd3s_report_id',
            'status': 'd3s_status',
            'real_time_ms': 'd3s_real_time_ms',
            'real_time_offset_ms': 'd3s_real_time_offset_ms',
            'dose': 'd3s_dose',
            'dose_rate': 'd3s_dose_rate',
            'dose_user_accum': 'd3s_dose_user_accum',
            'neutron_live_time': 'd3s_neutron_live_time',
            'neutron_count': 'd3s_neutron_count',
            'neutron_temperature': 'd3s_neutron_temperature',
            'gamma_live_time': 'd3s_gamma_live_time',
            'gamma_count': 'd3s_gamma_count',
            'gamma_temperature': 'd3s_gamma_temperature',
            'spectrum_bit_size': 'd3s_spectrum_bit_size',
        },
    },
}

inverted_topics_table = {key: (subsystem, sensor, parameter)
                         for subsystem, sensors in topics_table.items()
                         for sensor, parameters in sensors.items()
                         for parameter, key in parameters.items()}


def expand_topics(values):
    output = {}

    for k, v in values.items():
        try:
            output[inverted_topics_table[k]] = v
        except KeyError:
            continue

    return output
