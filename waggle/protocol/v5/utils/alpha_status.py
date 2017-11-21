# Conversion for alphasensor


def convert(value):
    if value['alpha_status'] == 1:
        value['alpha_status'] = ('on', 'No unit')
    else:
        value['alpha_status'] = ('off', 'No unit')

    return value