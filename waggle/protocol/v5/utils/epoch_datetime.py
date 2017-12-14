# Conversion from timeepoch to datetime

import time

def convert(value, format='%Y %m %d %H:%M:%S'):
    returns = {}
    for key, raw in value.items():
        returns[key] = (time.strftime(format, time.gmtime(raw)), 'UTC')
    
    return returns