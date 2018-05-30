# Conversion from int to bool

def convert(value):
    returns = {}
    for key, raw in value.items():
        if raw == 1 or raw == 'Y':
            returns[key] = (True, '')
        else:
            returns[key] = (False, '')

    return returns
