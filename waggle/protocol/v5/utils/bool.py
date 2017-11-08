# Conversion from int to bool

def convert(value):
    name = ''
    val = 0
    for key, raw in value.items():
        name = key
        val = raw
    raw_b = value[key]

    if raw_b == 1:
        return True
    else:
        return False
