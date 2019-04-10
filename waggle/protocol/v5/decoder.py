# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import logging
from .spec import spec
from . import format
from . import utils
import waggle.checksum

logger = logging.getLogger('waggle.protocol.v5')


HEADER_SIZE = 3
FOOTER_SIZE = 2
HEADER_BYTE = 0xaa
FOOTER_BYTE = 0x55


def decode_frame(frame, required_version=2):
    """Decode a frame
    @params:
        - A byte array of the frame
        - (optional) True for applying conversions
    @return:
        dict {sensorid: values, ...}
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Decoding datagram %s.', bytes(frame))

    data = bytearray()

    if not isinstance(frame, bytearray) and not isinstance(frame, bytes):
        raise TypeError('frame must be byte-like type object')

    while len(frame) != 0:
        header = frame[0]
        version = frame[1] & 0x0F
        length = frame[2]
        crc = frame[HEADER_SIZE + length]
        footer = frame[HEADER_SIZE + length + 1]
        subdata = frame[HEADER_SIZE:HEADER_SIZE + length]

        if header != HEADER_BYTE:
            raise RuntimeError('invalid start byte')

        if footer != FOOTER_BYTE:
            raise RuntimeError('invalid end byte')

        if version != required_version:
            raise RuntimeError('invalid protocol version: target version is %d' % (required_version,))

        if length != len(subdata):
            raise RuntimeError('invalid length')

        if crc != waggle.checksum.crc8(subdata):
            raise RuntimeError('invalid crc')

        subdata = frame[HEADER_SIZE + 1:HEADER_SIZE + length]
        data.extend(subdata)
        frame = frame[HEADER_SIZE + length + FOOTER_SIZE:]

    return unpack_results(data)


def unpack_results(data):
    results = {}

    for sensor_id, names, values in decode_data(data):
        if sensor_id not in results:
            results[sensor_id] = {}

        sensor_results = results[sensor_id]

        for name, value in zip(names, values):
            if name not in sensor_results:
                sensor_results[name] = value
            else:
                sensor_results[name] += value

    return results


spec_cache = {}

for sensor_id in spec.keys():
    params = spec[sensor_id]['params']

    names = tuple(param['name'] for param in params)
    formats = tuple(param['format'] for param in params)
    lengths = tuple(param['length'] for param in params)

    spec_cache[sensor_id] = (names, formats, lengths)


def decode_data(data):
    for sensor_id, sensor_data in get_data_subpackets(data):
        try:
            names, formats, lengths = spec_cache[sensor_id]

            if sensor_data is None:
                yield sensor_id, names, ['invalid'] * len(names)
            else:
                yield sensor_id, names, list(format.waggle_unpack(formats, lengths, sensor_data))
        except Exception as exc:
            logger.exception('Got an exception while decoding subpackets. sensor = {:02X}, data = {}'.format(sensor_id, repr(sensor_data)))
            continue


def get_data_subpackets(data):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Reading subpackets in body %s.', bytes(data))

    subpackets = []

    offset = 0

    while offset < len(data):
        logger.debug('Reading subpacket at offset %d.', offset)
        sensor_id = data[offset + 0]
        length = data[offset + 1] & 0x7F
        valid = data[offset + 1] & 0x80

        if sensor_id != 0x11:
            offset += 2
        else:
            offset += 1
            length += 1

        sensor_data = data[offset:offset + length]
        offset += length

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Read subpacket with sensor ID %s and data %s.', hex(sensor_id), bytes(sensor_data))

        if valid == 0x80:
            subpackets.append((sensor_id, sensor_data))
        else:
            subpackets.append((sensor_id, None))

    if offset != len(data):
        logger.warning('Subpacket total length differs from packet length.')

    return subpackets


def convert(values, sensor_id):
    if sensor_id not in spec:
        return values

    conversion_name = spec[sensor_id]['conversion']
    if conversion_name is None:
        raw_values = {}
        for key, value in values.items():
            raw_values[key] = (value, '')
        return raw_values

    try:
        module = getattr(utils, conversion_name)
        return module.convert(values)
    except AttributeError:
        logging.warning('No valid conversion loaded for %s' % (sensor_id,))
    return values
