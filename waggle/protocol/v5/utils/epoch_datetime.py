# Conversion from timeepoch to datetime

import time

def convert(value, format='%Y %m %d %H:%M:%S'):
    name = ''
    val = 0
    for key, raw in value.items():
        name = key
        val = raw
    raw_e = value[key]
    
    return time.strftime(format, time.gmtime(raw_e)), 'UTC'