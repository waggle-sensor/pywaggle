# Conversion for mma8452q in Metsense

def convert(value):
    raw_accx = value[0x07]['metsense_mma8452q_acc_x']
    raw_accy = value[0x07]['metsense_mma8452q_acc_y']
    raw_accz = value[0x07]['metsense_mma8452q_acc_z']

    gcount_x = raw_accx >> 4
    if (raw_accx >> 8) > 0x7F:
        gcount_x -= 0x1000
    accx = gcount_x / (1 << 12) / 4

    gcount_y = raw_accy >> 4
    if (raw_accy >> 8) > 0x7F:
        gcount_y -= 0x1000
    accy = gcount_y / (1 << 12) / 4

    gcount_z = raw_accy >> 4
    if (raw_accy >> 8) > 0x7F:
        gcount_z -= 0x1000
    accz = gcount_z / (1 << 12) / 4

    return accx, 'gx', accy, 'gy', accz, 'gz'