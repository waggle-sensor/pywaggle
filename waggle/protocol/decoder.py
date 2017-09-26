import logging
from spec import spec
import format
import utils
from crc import create_crc

logger = logging.getLogger('protocol.decoder')

'''
    Decode a frame
    @params:
        - A byte array of the frame
    @return:
        dict {sensorid: values, ...}
'''
def decode_frame(frame):
    if not isinstance(frame, bytearray) and not isinstance(frame, bytes):
        raise TypeError('frame must be byte-like type object')

    header = frame[0]
    length = frame[2]
    crc = frame[-2]
    footer = frame[-1]
    data = frame[3:-2]

    if header != 0xAA:
        raise RuntimeError('invalid start byte')

    if footer != 0x55:
        raise RuntimeError('invalid end byte')

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


def decode_data(data, auto_convert=True):
    for sensor_id, sensor_data in get_data_subpackets(data):
        try:
            params = spec[sensor_id]
            names = [param['name'] for param in params]
            conversions = [param['conversion'] for param in params]
            formats = ''.join([param['format'] for param in params])
            lengths = [param['length'] for param in params]
            values = []
            for name, conversion, value, in zip(names, conversions, format.waggle_unpack(formats, lengths, sensor_data)):
                if auto_convert:
                    if conversion is not None and conversion is not '':
                        value = convert(value, conversion)
                    
                values.append(value)
            yield sensor_id, names, values
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
    