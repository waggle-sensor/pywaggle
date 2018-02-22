# Conversion for chemsense
# chemsense version2, no data of IMU is comming from chemsense --> chemsense FW issue

import math

from waggle.protocol.v5.res import chemsense_calib_data

mid_dict = {}
imported_data = {}

def import_data():
    xl_data = {}

    rows = chemsense_calib_data.chemsense_calib_data_raw.strip().split('\n')
    for row in rows:
        rowValues = row.strip().split(';')
        chem_id = rowValues[1]

        xl_data[chem_id] = {
            'IRR': {'sensitivity': rowValues[-42], 'baseline40': rowValues[-21], 'Mvalue': rowValues[-7]},   # IRR = RESP, baseline = Izero@25C
            'IAQ': {'sensitivity': rowValues[-41], 'baseline40': rowValues[-20], 'Mvalue': rowValues[-6]},
            'SO2': {'sensitivity': rowValues[-40], 'baseline40': rowValues[-19], 'Mvalue': rowValues[-5]},
            'H2S': {'sensitivity': rowValues[-39], 'baseline40': rowValues[-18], 'Mvalue': rowValues[-4]},
            'OZO': {'sensitivity': rowValues[-38], 'baseline40': rowValues[-17], 'Mvalue': rowValues[-3]},
            'NO2': {'sensitivity': rowValues[-37], 'baseline40': rowValues[-16], 'Mvalue': rowValues[-2]},
            'CMO': {'sensitivity': rowValues[-36], 'baseline40': rowValues[-15], 'Mvalue': rowValues[-1]}
        }

    return xl_data


def key_unit(k):
    if 'T' in k:
        return 'C'
    if 'P' in k:
        return 'hPa'

    return '%RH'


def chemical_sensor(ky, IpA):
    global imported_data
    Tzero = 40.0

    if len(imported_data) == 0:
        imported_data = import_data()

    if mid_dict['BAD'] in imported_data:
        Tavg = (float(mid_dict['AT0']) + float(mid_dict['AT1']) + float(mid_dict['AT2']) + float(mid_dict['AT3'])) / 400.0

        sensitivity = float(imported_data[mid_dict['BAD']][ky]['sensitivity'])
        baseline = float(imported_data[mid_dict['BAD']][ky]['baseline40'])
        Minv = float(imported_data[mid_dict['BAD']][ky]['Mvalue'])

        InA = float(IpA)/1000.0 - baseline*math.exp((Tavg - Tzero) / Minv)
        converted = round(InA / sensitivity, 6)
        return converted, 'ppm'
    else:
        return IpA, 'raw'


def convert_pair(key, val):
    if 'BAD' in key:
        chem_id = val
        return 'id', val, ''
    if 'SH' in key or 'HD' in key or 'LP' in key or 'AT' in key or 'LT' in key:
        return key, float(val)/100.0, key_unit(key)
    if 'SVL' in key or 'SIR' in key or 'SUV' in key:
        return key, int(val), 'raw'
    if 'AC' in key or 'GY' in key or 'VIX' in key or 'OIX' in key:
        return key, int(val), 'raw'

    conv_val, unit = chemical_sensor(key, val)
    return key, conv_val, unit


def convert(value):
    global mid_dict

    chem_dict = {}
    mid_dict = {}
    for pair in value['chemsense_raw'].split():
        try:
            key, val = pair.split('=')
        except ValueError:
            continue

        # ignore sequence number
        if key == 'SQN':
            continue

        mid_dict[key] = val

    for key, value in mid_dict.items():
        k, v, u = convert_pair(key, value)
        chem_dict['chemsense_' + k.lower()] = (v, u)

    return chem_dict
