# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import logging
from . import format
from . import spec
from binascii import hexlify
import waggle.checksum

logger = logging.getLogger('coresense.utils')


def populate(results):
    try:
        tip_count = results['Rain Gauge']['tip_count']
        results['Rain Gauge']['rain_inches'] = float(tip_count) * 0.01
    except:
        pass

    try:
        dielectric = results['Soil Moisture']['dielectric']
        volumetric_water_content = 4.3e-6 * dielectric**3 - 5.5e-4 * dielectric**2 + 2.92e-2 * dielectric - 5.3e-2
        results['Soil Moisture']['volumetric_water_content'] = volumetric_water_content
    except:
        pass

    return results


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

    if crc != waggle.checksum.crc8(data):
        raise RuntimeError('invalid crc')

    # merge resulting entries
    results = {}

    for name, values in decode_coresense_data(data):
        if name not in results:
            results[name] = {}
        results[name].update(values)

    return populate(results)


def decode_coresense_data(data):
    for sensor_id, sensor_data in get_data_subpackets(data):
        try:
            name, fmt, fields = spec[sensor_id]
            data = dict(zip(fields, format.unpack(fmt, sensor_data)))
            yield name, data
        except KeyError:
            logger.warning('could not decode subpacket: id={:02X} data={}'.format(sensor_id, sensor_data))
            continue
        except Exception:
            logger.exception('Got an exception while decoding subpackets. sensor = {:02X}, format = {}, data = {}'.format(sensor_id, fmt, repr(sensor_data)))
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
