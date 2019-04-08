# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import logging
# import math
import re
import os
# from waggle.protocol.v5.res import chemsense_calib_data as chemsense_res
# from waggle.protocol.v5.res import chemsense_empty_data as chemsense_res
import csv
import numpy as np

logger = logging.getLogger('waggle.protocol.v5.utils.chemsense')

basis = ['IRR', 'IAQ', 'SO2', 'H2S', 'OZO', 'NO2', 'CMO']
basis_by_name = {name: i for i, name in enumerate(basis)}

humidity_sensors = ['HDH']
temperature_sensors = ['AT0', 'AT1', 'AT2', 'AT3', 'HDT', 'LPT', 'LTM']
pressure_sensors = ['LPP']
raw_sensors = ['SIR', 'SUV', 'SVL']


def slice(a, ks):
    return [a[k] for k in ks]


def slice_array(a, ks):
    return np.array(slice(a, ks))


def read_calib_data(path):
    results = {}

    with open(path) as file:
        reader = csv.DictReader(file)

        for row in reader:
            results[row['ID']] = [
                np.fromstring(row['S'], dtype=float, sep=' '),
                np.fromstring(row['Izero'], dtype=float, sep=' '),
                np.fromstring(row['n'], dtype=float, sep=' '),
                np.fromstring(row['M'], dtype=float, sep=' ').reshape(7, 7),
            ]

    return results


calib = read_calib_data(os.path.join(os.path.dirname(__file__), 'chemsense_calibration.csv'))


def advanced_filter(a, b):
    if a < 0.0 and b < 0.0:
        return 0.0, 0.0
    elif a > 0.0 and b < 0.0:
        return a + b, 0.0
    elif a < 0.0 and b > 0.0:
        return 0.0, a + b
    else:
        return a, b


def apply_corrections_to_sample(sample):
    '''
    The argument `sample` should be a dictionary with keys:

    * BAD - Board ID.
    * AT0, AT1, AT2, AT3 - Temperature readings.
    * IRR, IAQ, SO2, H2S, OZO, NO2, CMO - Chemical readings.
    '''
    S, Izero, n, M = calib[sample['BAD']]

    Tboard = slice_array(sample, ['AT0', 'AT1', 'AT2', 'AT3']).mean() / 100.0
    CurZero = Izero * np.exp((Tboard - 40.0) / n) * 1e3
    Cur = slice_array(sample, basis)
    uncorrectedPPB = (Cur - CurZero) / S
    correctedPPM = np.dot(M, uncorrectedPPB) / 1000.0

    i = basis_by_name['OZO']
    j = basis_by_name['NO2']
    correctedPPM[i], correctedPPM[j] = advanced_filter(correctedPPM[i], correctedPPM[j])

    return dict(zip(basis, correctedPPM))


# def import_data():
#     xl_data = {}
#
#     rows = chemsense_res.calib_data.strip().splitlines()
#
#     for row in rows:
#         fields = row.strip().split(';')
#         chem_id = fields[1].lower()
#
#         xl_data[chem_id] = {
#             # IRR = RESP, baseline = Izero@25C
#             'IRR': {'sensitivity': fields[-42], 'baseline40': fields[-21], 'Mvalue': fields[-7]},
#             'IAQ': {'sensitivity': fields[-41], 'baseline40': fields[-20], 'Mvalue': fields[-6]},
#             'SO2': {'sensitivity': fields[-40], 'baseline40': fields[-19], 'Mvalue': fields[-5]},
#             'H2S': {'sensitivity': fields[-39], 'baseline40': fields[-18], 'Mvalue': fields[-4]},
#             'OZO': {'sensitivity': fields[-38], 'baseline40': fields[-17], 'Mvalue': fields[-3]},
#             'NO2': {'sensitivity': fields[-37], 'baseline40': fields[-16], 'Mvalue': fields[-2]},
#             'CMO': {'sensitivity': fields[-36], 'baseline40': fields[-15], 'Mvalue': fields[-1]},
#         }
#
#     return xl_data
#
#
# imported_data = None
#
#
# def get_imported_data():
#     global imported_data
#
#     if imported_data is None:
#         imported_data = import_data()
#
#     return imported_data
#
#
# def get_instance_data(instance_id):
#     imported_data = get_imported_data()
#
#     try:
#         return imported_data[instance_id]
#     except KeyError:
#         logger.warning('No instance_id %s in calibration data.')
#         raise
#
#
# def key_unit(k):
#     if 'T' in k:
#         return 'C'
#     if 'P' in k:
#         return 'hPa'
#
#     return '%RH'
#
#
# def chemical_sensor(ky, IpA, mid_dict):
#     instance_id = mid_dict['BAD'].lower()
#
#     try:
#         instance_data = get_instance_data(instance_id)
#     except KeyError:
#         return [(IpA, 'raw')]
#
#     coeffs = instance_data[ky]
#
#     AT = [
#         float(mid_dict['AT0']),
#         float(mid_dict['AT1']),
#         float(mid_dict['AT2']),
#         float(mid_dict['AT3']),
#     ]
#
#     Tavg = sum(AT) / 400.0
#     Tzero = 40.0
#
#     sensitivity = float(coeffs['sensitivity'])
#     baseline = float(coeffs['baseline40'])
#     Minv = float(coeffs['Mvalue'])
#
#     InA = float(IpA)/1000.0 - baseline*math.exp((Tavg - Tzero) / Minv)
#     converted = InA / sensitivity
#
#     return [
#         (IpA, 'raw'),
#         (round(converted, 6), 'ppm'),
#     ]
#
#
# def convert_pair(key, val, mid_dict):
#     if key == 'SQN':
#         return 'sqn', []
#
#     if key == 'BAD':
#         return 'id', (val.lower(), '')
#
#     if 'SH' in key or 'HD' in key or 'LP' in key or 'AT' in key or 'LT' in key:
#         v = float(val)
#         return key, [
#             (v, 'raw'),
#             (v/100.0, key_unit(key)),
#         ]
#
#     if 'SVL' in key or 'SIR' in key or 'SUV' in key:
#         return key, (int(val), 'raw')
#
#     if 'AC' in key or 'GY' in key or 'VIX' in key or 'OIX' in key:
#         return key, (int(val), 'raw')
#
#     return key, chemical_sensor(key, val, mid_dict)


chemsense_pattern = re.compile(r'(\S+)=(\S+)')


def convert(value):
    sample = dict(chemsense_pattern.findall(value['chemsense_raw']))

    for k in sample.keys():
        try:
            sample[k] = float(sample[k])
        except ValueError:
            continue

    correctedPPM = apply_corrections_to_sample(sample)

    results = {}

    results['chemsense_id'] = [(sample['BAD'].lower(), '')]
    results['chemsense_sqn'] = []

    for s in humidity_sensors:
        results['chemsense_' + s.lower()] = [
            (sample[s], 'raw'),
            (sample[s] / 100.0, '%RH'),
        ]

    for s in temperature_sensors:
        results['chemsense_' + s.lower()] = [
            (sample[s], 'raw'),
            (sample[s] / 100.0, 'C'),
        ]

    for s in pressure_sensors:
        results['chemsense_' + s.lower()] = [
            (sample[s], 'raw'),
            (sample[s] / 100.0, 'hPa'),
        ]

    for s in basis:
        results['chemsense_' + s.lower()] = [
            (sample[s], 'raw'),
            (correctedPPM[s], 'ppm'),
        ]

    for s in raw_sensors:
        results['chemsense_' + s.lower()] = [
            (int(sample[s]), 'raw'),
        ]

    return results

    # chem_dict = {}
    #
    # for key, value in sample.items():
    #     newkey, results = convert_pair(key, value, sample)
    #     chem_dict['chemsense_' + newkey.lower()] = results
    #
    # return chem_dict


if __name__ == '__main__':
    test_data = [
        {'chemsense_raw': 'BAD=5410EC38B7F4 SQN=0 SHT=641 SHH=6409 HDT=604 HDH=6484 LPT=820 LPP=100455 SUV=5 SVL=269 SIR=259 BAD=5410EC38B7F4 SQN=1 IRR=3622 IAQ=4411 SO2=-2285 H2S=-256 OZO=3469 NO2=549 CMO=1143 BAD=5410EC38B7F4 SQN=2 AT0=569 AT1=615 AT2=693 AT3=751 LTM=6554 '},
        {'chemsense_raw': 'BAD=5410EC38B7F4 SQN=14 SHT=637 SHH=6422 HDT=599 HDH=6484 LPT=816 LPP=100456 SUV=0 SVL=258 SIR=262 BAD=5410EC38B7F4 SQN=15 IRR=3772 IAQ=4639 SO2=-627 H2S=-434 OZO=3333 NO2=778 CMO=1709 BAD=5410EC38B7F4 SQN=16 AT0=569 AT1=615 AT2=693 AT3=751 LTM=6554 '},
        {'chemsense_raw': '0 HDT=597 HDH=6523 LPT=815 LPP=100459 SUV=2 SVL=261 SIR=267 BAD=5410EC38B7F4 SQN=29 IRR=3881 IAQ=3765 SO2=-1298 H2S=-850 OZO=1913 NO2=1360 CMO=755 BAD=5410EC38B7F4 SQN=2A AT0=562 AT1=606 AT2=682 AT3=739 LTM=6592 '},
        {'chemsense_raw': '0 HDT=597 HDH=6523 LPT=815 LPP=100459 SUV=2 SVL=261 SIR=267 BAD=5410EC38B7F4 SQN=29 IRR=3881 IAQ=3765 SO2=-1298 H2S=-850 OZO=1913 NO2=1360 CMO=755 BAD=5410EC38B7F4 SQN=2A AT0=562 AT1=606 AT2=682 AT3=739 LTM=6592 '}
    ]

    for v in test_data:
        convert(v)
