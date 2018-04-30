# Conversion for alphasensor

def convert_firmware(fw):
    major = fw[0]
    minor = fw[1]

    if major == 255:
        return None, ''

    return str(major) + '.' + str(minor), ''


def convert_serial(s):
    if s is None:
        return None, ''

    if 'OPC' not in s:
        return None, ''

    return s, ''

def convert(value):
    try:
        value['alpha_firmware'] = convert_firmware(value['alpha_firmware'])
    except KeyError:
        pass

    try:
        value['alpha_serial'] = convert_serial(value['alpha_serial'])
    except KeyError:
        pass

    return value
