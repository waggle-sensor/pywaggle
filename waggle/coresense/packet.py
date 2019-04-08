# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import waggle.checksum

def decode_packet(data):
    header = data[0]
    version = (data[1] & 0xF0) >> 4
    length = data[2]
    body = data[3:-2]
    crc = data[-2]
    footer = data[-1]

    if header != 0xAA:
        raise RuntimeError('Invalid start byte.')

    if footer != 0x55:
        raise RuntimeError('Invalid end byte.')

    if length != len(body):
        raise RuntimeError('Invalid length.')

    if crc != waggle.checksum.crc8(body):
        raise RuntimeError('Invalid CRC.')

    return {
        'version': version,
        'body': body,
        'subpackets': decode_packet_body(body)
    }


def decode_packet_body(body):
    subpackets = []

    offset = 0

    while offset < len(body):
        sensor_id = body[offset + 0]
        length = body[offset + 1] & 0x7F
        valid = body[offset + 1] & 0x80 == 0x80
        offset += 2

        sensor_data = body[offset:offset+length]
        offset += length

        subpackets.append({
            'id': sensor_id,
            'valid': valid,
            'body': sensor_data
        })

    if offset != len(body):
        raise RuntimeError('Total subpacket length different than data size.')

    return subpackets
