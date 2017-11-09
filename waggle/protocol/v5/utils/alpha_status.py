# Conversion for alphasensor


def convert(value):
    if value['alpha_status'] == 1:
        value['alpha_status'] = 'on'
    else:
        value['alpha_status'] = 'off'

    return value