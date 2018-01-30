# Conversion for alphasensor

def convert(value):
    for key in value:
        if key == 'alpha_firmware':
            raw_f = value['alpha_firmware']
            version = str(raw_f[0]) + '.' + str(raw_f[1])
            value['alpha_firmware'] = (version, '')
        elif key == 'alpha_serial':
            raw_s = value['alpha_serial']
            value['alpha_serial'] = (raw_s, '')

    return value
