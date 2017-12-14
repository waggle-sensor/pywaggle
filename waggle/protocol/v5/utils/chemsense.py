# Conversion for chemsense
# chemsense version2, no data of IMU is comming from chemsense --> chemsense FW issue


def key_unit(k):
    if 'T' in k:
        return 'C'
    if 'P' in k:
        return 'hPa'
    return '%RH'


def convert_pair(key, val):
    if 'BAD' in key:
        return 'id', val, 'mac'
    if 'SH' in key or 'HD' in key or 'LP' in key or 'AT' in key or 'LT' in key:
        return key, float(val)/100.0, key_unit(key)
    if 'SVL' in key or 'SIR' in key or 'SUV' in key:
        return key, val, 'raw'
    return key, int(val), 'raw'


def convert(value):
    raw_s = value['chemsense_raw']

    chem_dict = {}

    for pair in raw_s.split():
        try:
            key, val = pair.split('=')
        except ValueError:
            continue

        # ignore sequence number
        if key == 'SQN':
            continue

        k, v, u = convert_pair(key, val)
        chem_dict['chemsense_' + k.lower()] = (v, u)

    return chem_dict
