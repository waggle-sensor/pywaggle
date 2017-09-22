import logging
from spec import spec
import format

logger = logging.getLogger('protocol.encoder')

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

    total_length = 0.0 # in byte
    for index, param in enumerate(params):
        print(param)
        value = data[index]
        param_length = param['length']
        param_format = param['format']
        yield format.pack(param_format, value)


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

    subpackets = []
    for sub_id in frame_data:
        assert isinstance(sub_id, int)

        sub_values = frame_data[sub_id]
        encoded = encode_sub_packet(sub_id, sub_values)
        if encoded is not None:
            subpackets.extend(encoded)

    return subpackets

d = {0x58: [123,]}
encoded = encode_frame(d)
print(encoded)
