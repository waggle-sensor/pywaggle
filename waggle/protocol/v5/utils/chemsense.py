#############################################################################################################################################################
#
# Conversion for chemsense
# Conversion of chemical sensors are not going through in this code, because the same procedure is processed in other place, maybe beehive server (May 2018)
#
# If you want to revive chemical sensor conversion in here, then change:
# from waggle.protocol.v5.res import chemsense_empty_data >> import empty dataset to
# from waggle.protocol.v5.res import chemsense_calib_data.py >> import the correct dataset for each chemical sensors calibration
#
#############################################################################################################################################################

import math
import re
# from waggle.protocol.v5.res import chemsense_empty_data as chemsense_res
from waggle.protocol.v5.res import chemsense_calib_data as chemsense_res

# mid_dict = {}
imported_data = None


def import_data():
    xl_data = {}

    rows = chemsense_res.calib_data.strip().splitlines()

    for row in rows:
        fields = row.strip().split(';')
        chem_id = fields[1].lower()

        xl_data[chem_id] = {
            # IRR = RESP, baseline = Izero@25C
            'IRR': {'sensitivity': fields[-42], 'baseline40': fields[-21], 'Mvalue': fields[-7]},
            'IAQ': {'sensitivity': fields[-41], 'baseline40': fields[-20], 'Mvalue': fields[-6]},
            'SO2': {'sensitivity': fields[-40], 'baseline40': fields[-19], 'Mvalue': fields[-5]},
            'H2S': {'sensitivity': fields[-39], 'baseline40': fields[-18], 'Mvalue': fields[-4]},
            'OZO': {'sensitivity': fields[-38], 'baseline40': fields[-17], 'Mvalue': fields[-3]},
            'NO2': {'sensitivity': fields[-37], 'baseline40': fields[-16], 'Mvalue': fields[-2]},
            'CMO': {'sensitivity': fields[-36], 'baseline40': fields[-15], 'Mvalue': fields[-1]},
        }

    return xl_data


def key_unit(k):
    if 'T' in k:
        return 'C'
    if 'P' in k:
        return 'hPa'

    return '%RH'


def chemical_sensor(ky, IpA, mid_dict):
    global imported_data

    if imported_data is None:
        imported_data = import_data()

    try:
        coeffs = imported_data[mid_dict['BAD']][ky]
    except KeyError:
        return IpA, 'raw'

    AT = [
        float(mid_dict['AT0']),
        float(mid_dict['AT1']),
        float(mid_dict['AT2']),
        float(mid_dict['AT3']),
    ]

    Tavg = sum(AT) / 400.0
    Tzero = 40.0

    sensitivity = float(coeffs['sensitivity'])
    baseline = float(coeffs['baseline40'])
    Minv = float(coeffs['Mvalue'])

    InA = float(IpA)/1000.0 - baseline*math.exp((Tavg - Tzero) / Minv)
    converted = InA / sensitivity

    return round(converted, 6), 'ppm'


def convert_pair(key, val, mid_dict):
    if 'BAD' in key:
        chem_id = val.lower()
        return 'id', chem_id, ''
    if 'SH' in key or 'HD' in key or 'LP' in key or 'AT' in key or 'LT' in key:
        return key, float(val)/100.0, key_unit(key)
    if 'SVL' in key or 'SIR' in key or 'SUV' in key:
        return key, int(val), 'raw'
    if 'AC' in key or 'GY' in key or 'VIX' in key or 'OIX' in key:
        return key, int(val), 'raw'

    conv_val, unit = chemical_sensor(key, val, mid_dict)
    return key, conv_val, unit


chemsense_pattern = re.compile(r'(\S+)=(\S+)')


def convert(value):
    mid_dict = dict(chemsense_pattern.findall(value['chemsense_raw']))

    chem_dict = {}

    for key, value in mid_dict.items():
        k, v, u = convert_pair(key, value, mid_dict)
        chem_dict['chemsense_' + k.lower()] = (v, u)

    return chem_dict
