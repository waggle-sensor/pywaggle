import logging
from . import format
from . import spec


logging.basicConfig(level=logging.WARN)


def decode_frame(frame):
    if frame[0] != 0xAA:
        raise RuntimeError('invalid frame start {:02X}'.format(frame[0]))

    if frame[-1] != 0x55:
        raise RuntimeError('invalid frame end {:02X}'.format(frame[-1]))

    if frame[2] + 5 != len(frame):
        raise RuntimeError('inconsistent frame length')

    return dict(decode_coresense_data(frame[3:-3]))


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
