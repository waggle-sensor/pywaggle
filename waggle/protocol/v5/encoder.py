import logging
import math
from .spec import spec
from . import format
from .crc import create_crc

logger = logging.getLogger('protocol.encoder')
sequence = 0
coresense_sequence = 0

# protocol_version 1 is used in lower or equal to coresense firmware 3.12
protocol_version = 2

'''
    Encode a sub packet
    @params:
        id - ID of the sub packet
        data - A list of parameters for the ID
    @return:
        A binary type sub packet
        None when failed
'''
def encode_sub_packet(id, data=[]):
    try:
        params = spec[id]['params']
    except KeyError:
        logger.error('ID %d is unknown' % (id,))
        return None

    if not isinstance(data, list):
        logger.error('%s must be a list' % (str(data),))
        return None

    if len(params) != len(data):
        logger.error('Length of the %s must be matched' % (str(data),))
        return None

    formats = ''.join([param['format'] for param in params])
    lengths = [param['length'] for param in params]
    binary = format.waggle_pack(formats, lengths, data)

    packet_length = len(binary)
    sub_packet = bytearray(2)
    sub_packet[0] = id
    sub_packet[1] = 0x80 | packet_length
    sub_packet.extend(binary)

    return sub_packet

'''
    Encode a frame
    @params:
        - dict {sensorid: values, ...}
    @return:
        A byte array of the frame
'''
def encode_frame(frame_data):
    if not isinstance(frame_data, dict):
        logger.error('%s must be a dictionary' % (str(frame_data),))
        return None

    bodies = []
    body = bytearray()
    max_body_length = pow(2, 8) - 1
    for sub_id in frame_data:
        assert isinstance(sub_id, int)

        sub_values = frame_data[sub_id]
        encoded = encode_sub_packet(sub_id, sub_values)

        if encoded is not None:
            if len(body) + len(encoded) > max_body_length:
                bodies.append(body)
                body = bytearray()
            body.extend(encoded)

    bodies.append(body)

    body_length = len(body)
    waggle_packet = bytearray()
    packet_type = 0 # sensor reading
    for index, body in enumerate(bodies):
        body_length = len(body)

        header = bytearray(3)
        header[0] = 0xAA
        header[1] = ((packet_type & 0x0F) << 4) | protocol_version & 0x0F
        header[2] = body_length + 1

        packet_body = bytearray(1)
        if index + 1 == len(bodies):
            packet_body[0] = index | 0x80
        else:
            packet_body[0] = index
        packet_body.extend(body)

        footer = bytearray(2)
        footer[0] = create_crc(packet_body)
        footer[1] = 0x55

        waggle_packet.extend(header)
        waggle_packet.extend(packet_body)
        waggle_packet.extend(footer)

        if sequence < 0x7F:
            sequence += 1
        else:
            sequence = 0

    return bytes(waggle_packet)


def coresense_encode_frame(sensors):
    # Packaging
    buffer = bytearray()
    for i in range(0,len(sensors), 2):
        data.append(sensors[i]) # call function type
        if (sensors[i] == 0x05):
            data.append(0x01) # ack --> 0 1bit, 7-bit parameter length
            data.append(sensors[i + 1])

    return buffer