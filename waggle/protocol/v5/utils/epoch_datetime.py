# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion from timeepoch to datetime

import time

def convert(value, format='%Y %m %d %H:%M:%S'):
    returns = {}

    for key, raw in value.items():
        returns[key] = (time.strftime(format, time.gmtime(raw)), 'UTC')

    return returns
