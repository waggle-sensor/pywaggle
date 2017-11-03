import logging
from .spec import spec
from . import format
from . import utils
from .crc import create_crc

logger = logging.getLogger('protocol.decoder')

'''
    Decode a frame
    @params:
        - A byte array of the frame
        - (optional) True for applying conversions
    @return:
        dict {sensorid: values, ...}
'''
def decode_frame(frame, required_version=2):
    if not isinstance(frame, bytearray) and not isinstance(frame, bytes):
        raise TypeError('frame must be byte-like type object')

    header = frame[0]
    packet_type = (frame[1] >> 4) & 0x0F
    version =  frame[1] & 0x0F
    sequence_number = frame[2]
    length = frame[3]
    crc = frame[-2]
    footer = frame[-1]
    data = frame[4:-2]

    if header != 0xAA:
        raise RuntimeError('invalid start byte')

    if footer != 0x55:
        raise RuntimeError('invalid end byte')

    if version != required_version:
        raise RuntimeError('invalid protocol version: target version is %d' % (required_version,))

    if length != len(frame) - 5:
        raise RuntimeError('invalid length')

    if crc != create_crc(data):
        raise RuntimeError('invalid crc')

    # merge resulting entries
    results = {}

    for sensor_id, names, values in decode_data(data):
        if sensor_id not in results:
            results[sensor_id] = {}
        
        for name, value in zip(names, values):
            results[sensor_id][name] = value

    return results


def decode_data(data):
    for sensor_id, sensor_data in get_data_subpackets(data):
        try:
            params = spec[sensor_id]
            names = [param['name'] for param in params]
            conversions = [param['conversion'] for param in params]
            formats = ''.join([param['format'] for param in params])
            lengths = [param['length'] for param in params]

            yield sensor_id, names, format.waggle_unpack(formats, lengths, sensor_data)
        except KeyError:
            logger.warning('could not decode subpacket: id={:02X} data={}'.format(sensor_id, hexlify(sensor_data).decode()))
            continue
        except Exception:
            logger.exception('Got an exception while decoding subpackets. sensor = {:02X}, data = {}'.format(sensor_id, repr(sensor_data)))
            continue


def get_data_subpackets(data):
    subpackets = []

    offset = 0

    while offset < len(data):
        sensor_id = data[offset + 0]
        length = data[offset + 1] & 0x7F
        valid = data[offset + 1] & 0x80 == 0x80
        offset += 2

        sensor_data = data[offset:offset + length]
        offset += length

        if valid:
            subpackets.append((sensor_id, sensor_data))

    if offset != len(data):
        logger.warning('Subpacket lengths do not total to payload length! offset = {}, length = {}'.format(offset, len(data)))

    return subpackets

def convert(value, name):
    try:
        module = getattr(utils, name)
        return module.convert(value)
    except AttributeError:
        logging.warning('No valid conversion loaded for %s' % (name,))
    return value
    
