import logging
from .spec import spec
import .format
from .crc import create_crc

logger = logging.getLogger('protocol.encoder')

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
        params = spec[id]
    except KeyError:
        logger.error('ID %d is unknown')
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

    body = bytearray()
    for sub_id in frame_data:
        assert isinstance(sub_id, int)

        sub_values = frame_data[sub_id]
        encoded = encode_sub_packet(sub_id, sub_values)
        
        if encoded is not None:
            body.extend(encoded)


    header = bytearray(3)
    header[0] = 0xAA
    
    body_length = len(body)
    assert body_length < pow(2, 8)
    sequence_number = 0
    header[1] = ((sequence_number & 0x0F) << 4) | protocol_version & 0x0F
    header[2] = body_length & 0xFF

    footer = bytearray(2)
    footer[0] = create_crc(body)
    footer[1] = 0x55

    return bytes(header + body + footer)
