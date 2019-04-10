# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for mma8452q in Metsense

def convert(value):
    raw = []
    raw.append(value['metsense_mma8452q_acc_x'])
    raw.append(value['metsense_mma8452q_acc_y'])
    raw.append(value['metsense_mma8452q_acc_z'])

    for i in range(len(raw)):
        gcount = raw[i] >> 4
        if (raw[i] >> 8) > 0x7F:
            gcount -= 0x1000
        raw[i] = gcount / ((1 << 12) / 4)
        raw[i] = round(raw[i]*1000, 3)

    value['metsense_mma8452q_acc_x'] = (raw[0], 'mg')
    value['metsense_mma8452q_acc_y'] = (raw[1], 'mg')
    value['metsense_mma8452q_acc_z'] = (raw[2], 'mg')

    return value
