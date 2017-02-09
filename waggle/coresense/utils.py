import logging
from . import format
from . import spec


logging.basicConfig(level=logging.WARN)


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

    if crc != crc8(data):
        raise RuntimeError('invalid crc')

    # merge resulting entries
    results = {}

    for name, values in decode_coresense_data(data):
        if name not in results:
            results[name] = {}
        results[name].update(values)

    return results


def decode_coresense_data(data):
    for sensor_id, sensor_data in get_data_subpackets(data):
        try:
            name, fmt, fields = spec[sensor_id]
            data = dict(zip(fields, format.unpack(fmt, sensor_data)))
            yield name, data
        except KeyError:
            pass
        except Exception:
            logging.exception('Got an exception while decoding subpackets. sensor = {:02X}, format = {}, data = {}'.format(sensor_id, fmt, repr(sensor_data)))


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
        logging.warn('Subpacket lengths do not total to payload length! offset = {}, length = {}'.format(offset, len(data)))

    return subpackets


def crc8(data, crc=0):
    for i in range(len(data)):
        crc ^= data[i]
        for j in range(8):
            if crc & 1 != 0:
                crc = (crc >> 1) ^ 0x8C
            else:
                crc >>= 1
    return crc
