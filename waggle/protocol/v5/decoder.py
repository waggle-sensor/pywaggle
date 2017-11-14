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
    HEADER_SIZE = 4
    FOOTER_SIZE = 2
    data = bytearray()

    if not isinstance(frame, bytearray) and not isinstance(frame, bytes):
        raise TypeError('frame must be byte-like type object')

    while len(frame) != 0:
        header = frame[0]
        packet_type = (frame[1] >> 4) & 0x0F
        version =  frame[1] & 0x0F
        sequence_number = frame[2] & 0x7F
        length = frame[3]
        crc = frame[HEADER_SIZE + length]
        footer = frame[HEADER_SIZE + length + 1]
        subdata = frame[HEADER_SIZE:HEADER_SIZE + length]

        if header != 0xAA:
            raise RuntimeError('invalid start byte')

        if footer != 0x55:
            raise RuntimeError('invalid end byte')

        if version != required_version:
            raise RuntimeError('invalid protocol version: target version is %d' % (required_version,))

        if length != len(subdata):
            raise RuntimeError('invalid length')

        if not check_crc(crc, subdata):
            raise RuntimeError('invalid crc')

        data.extend(subdata)
        frame = frame[HEADER_SIZE + length + FOOTER_SIZE:]

    # merge resulting entries
    results = {}

    for sensor_id, names, values in decode_data(data):
        if sensor_id not in results:
            results[sensor_id] = {}

        for name, value in zip(names, values):
            if name not in results[sensor_id]:
                results[sensor_id][name] = value
            else:
                results[sensor_id][name] += value


    return results


def decode_data(data):
    for sensor_id, sensor_data in get_data_subpackets(data):
        try:
            params = spec[sensor_id]['params']
            names = [param['name'] for param in params]
            formats = ''.join([param['format'] for param in params])
            lengths = [param['length'] for param in params]

            if sensor_data is None:
                yield sensor_id, names, ['invalid']*len(names)
                continue

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
        valid = data[offset + 1] & 0x80
        offset += 2

        sensor_data = data[offset:offset + length]
        offset += length

        if valid == 0x80:
            subpackets.append((sensor_id, sensor_data))
        else:
            subpackets.append((sensor_id, None))

    if offset != len(data):
        logger.warning('Subpacket lengths do not total to payload length! offset = {}, length = {}'.format(offset, len(data)))

    return subpackets

def convert(values, sensor_id):
    if not sensor_id in spec:
        return values

    conversion_name = spec[sensor_id]['conversion']
    if conversion_name is None:
        return values
    
    try:
        module = getattr(utils, conversion_name)
        return module.convert(values)
    except AttributeError:
        logging.warning('No valid conversion loaded for %s' % (sensor_id,))
    return values
    
def check_crc(crc, data):
    return True if crc == create_crc(data) else False

