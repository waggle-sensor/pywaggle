# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for alphasensor


def convert(value):
    if value['alpha_status'] == 1:
        value['alpha_status'] = ('on', '')
    else:
        value['alpha_status'] = ('off', '')

    return value
