# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
# Conversion from int to bool

def convert(value):
    returns = {}
    for key, raw in value.items():
        if raw == 1 or raw == 'Y':
            returns[key] = (True, '')
        else:
            returns[key] = (False, '')

    return returns
