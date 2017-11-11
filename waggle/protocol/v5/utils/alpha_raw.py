# Conversion for alphasensor


def convert(value):
    raw_f = value['alpha_firmware']

    version = str(raw_f[0]) + '.' + str(raw_f[1])
    value['alpha_firmware'] = version

    return value