# CRC utility

def create_crc(data):
    crc = 0x00

    for value in data:
        crc ^= value
        for i in range(0, 8):
            if crc & 0x01 == 1:
                crc = (crc >> 1) ^ 0x8C
            else:
                crc = crc >> 1
    return crc
