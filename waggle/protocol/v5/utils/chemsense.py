# Conversion for chemsense
# chemsense version2, no data of IMU is comming from chemsense --> chemsense FW issue

import math
import dataset
import xlrd

def import_chem_cali_data(id):
    # directory of the sensor calibration data
    directory = "/home/sager/Downloads/calib_data.xlsx"

    db = dataset.connect()
    xl = xlrd.open_workbook(directory, "rb")

    M = [16.94, 11.54, 13.83, 12.62, 'inf', 'inf', 12.02]
    # IRR[0], IAQ[1], SO2[2], H2S[3], OZO[4], NO2[5], CMO[6]
    # RESP, IAQ, SO2, H2S, OZO, NO2, CMO

    spec = {}

    for i, sheet in enumerate(xl.sheets()):
        for rownum in range(sheet.nrows):
            rowValues = sheet.row_values(rownum)
            # if '088' in str(rowValues[0]):
            if id == str(rowValues[1]):
                spec[str(rowValues[1])] = {
                    'RESP':{'sensitivity': rowValues[9], 'baseline': rowValues[23], 'Mvalue': 16.94},
                    'IAQ': {'sensitivity': rowValues[10], 'baseline': rowValues[24], 'Mvalue': 11.54},
                    'SO2': {'sensitivity': rowValues[11], 'baseline': rowValues[25], 'Mvalue': 13.83},
                    'H2S': {'sensitivity': rowValues[12], 'baseline': rowValues[26], 'Mvalue': 12.62},
                    'OZO': {'sensitivity': rowValues[13], 'baseline': rowValues[27], 'Mvalue': 'inf'},
                    'NO2': {'sensitivity': rowValues[14], 'baseline': rowValues[28], 'Mvalue': 'inf'},
                    'CMO': {'sensitivity': rowValues[15], 'baseline': rowValues[29], 'Mvalue': 12.02}
                }
            else:
                spec[id] = 'none'

    # print(spec)
    return spec

chem_id = ''
chem_dict = {}
zero_temp = 25

def key_unit(k):
    if 'T' in k:
        return 'C'
    if 'P' in k:
        return 'hPa'
    return '%RH'


def chemical_sensor(ky, instant_current):
    # check if the chemsense id is in the chem_cali_dic
    spec = import_chem_cali_data(chem_id)

    if spec[chec_id] != 'none':
        instant_temp = (chem_dict['chemsense_hdt'] + chem_dict['chemsense_sht'] + chem_dict['chemsense_lpt']) / 3.0

        sensitivity = spec[chem_id][ky]['sensitivity']
        baseline = spec[chem_id][ky]['baseline']
        M_value = spec[chem_id][ky]['Mvalue']

        if M_value == 'inf':
            corrected = instant_current - baseline
        else:
            corrected = instant_current - baseline * math.exp((instant_temp - zero_temp) / M_value)

        return ky, corrected, 'ppm'
    else:
        return ky, instant_current, 'raw'


def convert_pair(key, val):
    if 'BAD' in key:
        chem_id = val
        return 'id', val, ''
    if 'SH' in key or 'HD' in key or 'LP' in key or 'AT' in key or 'LT' in key:
        return key, float(val)/100.0, key_unit(key)
    if 'SVL' in key or 'SIR' in key or 'SUV' in key:
        return key, val, 'raw'
    if 'AC' in key or 'GY' in key or 'VIX' in key or 'OIX' in key:
        return key, int(val), 'raw'
    conv_val, unit = chemical_sensor(key, val)
    return key, conv_val, unit


def convert(value):
    chem_dict = {}
    for pair in value['chemsense_raw'].split():
        try:
            key, val = pair.split('=')
        except ValueError:
            continue

        # ignore sequence number
        if key == 'SQN':
            continue

        chem_dict['chemsense_' + key.lower()] = val

    for key, value in chem_dict.items():
        k, v, u = convert_pair(key, val)
        chem_dict['chemsense_' + k.lower()] = (v, u)

    return chem_dict
