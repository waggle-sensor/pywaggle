# Conversion from timeepoch to datetime

import time

def convert(value, format='%Y %m %d %H:%M:%S'):
    return time.strftime(format, time.gmtime(value)), 'UTC'