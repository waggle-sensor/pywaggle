# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
'''
Library for working with coresense data formats.

Example

>>> import format

>>> data = format.waggle_pack(['int', 'uint', 'hex', 'epoch'], [1, 1, 2, 4], [-32, 55, 'abcd', 1506703931])
>>> print([e for e in format.waggle_unpack('abcd', [1, 1, 2, 4], data)])

Format Reference

- float_2: fixed point (-127.99, 127.99)
- float_3: fixed point (-31.999, 31.999)

'''
import logging
from math import ceil
from bitstring import BitArray

logger = logging.getLogger('waggle.protocol.v5.format')


def pack_unsigned_int(value, length):
    return value.to_bytes(length, 'big')


def unpack_unsigned_int(buffer, offset, length):
    return int.from_bytes(buffer[offset:offset+length], 'big')


def pack_signed_int(value, length):
    return value.to_bytes(length, 'big', signed=True)


def unpack_signed_int(buffer, offset, length):
    return int.from_bytes(buffer[offset:offset+length], 'big', signed=True)


def pack_float(value, length):
    assert int(length) == 4 or int(length) == 8
    assert isinstance(value, float)
    return BitArray(float=value, length=to_bit(length)).bytes


def unpack_float(buffer, offset, length):
    value = BitArray(bytes=buffer, length=to_bit(
        length), offset=to_bit(offset))
    return value.float


def pack_hex_string(value, length):
    return bytes.fromhex(value)[:length]


def unpack_hex_string(buffer, offset, length):
    return buffer[offset:offset+length].hex()


pack_time_epoch = pack_unsigned_int
unpack_time_epoch = unpack_unsigned_int


def pack_float_format6(value, length=2.0):
    assert -127.99 <= value <= 127.99

    absvalue = abs(value)
    intpart = int(absvalue)
    fracpart = int(100 * round(absvalue - intpart, 2))
    packed = ((intpart & 0x7F) << 8) | fracpart & 0x7F
    if value < 0:
        packed |= 0x8000

    return BitArray(uint=packed, length=to_bit(length)).bytes


def unpack_float_format6(buffer, offset, length=2.0):
    byte1 = buffer[offset + 0]
    byte2 = buffer[offset + 1]
    # have to be careful here, we do not want three decimal placed here.
    value = (byte1 & 0x7F) + (((byte2 & 0x7F) % 100) * 0.01)
    if (byte1 & 0x80) == 0x80:
        value = value * -1
    return value


def pack_float_format8(value, length=2.0):
    assert -31.999 <= value <= 31.999

    absvalue = abs(value)
    intpart = int(absvalue)
    fracpart = int(1000 * round(absvalue - intpart, 3))

    packed = (((intpart & 0b00011111) << 2) | (
        (fracpart >> 8) & 0b00000011)) << 8
    packed |= fracpart & 0xFF

    if value < 0:
        packed |= 0x80
    return BitArray(uint=packed, length=to_bit(length)).bytes


def unpack_float_format8(buffer, offset, length=2.0):
    byte1 = buffer[offset + 0]
    byte2 = buffer[offset + 1]
    value = ((byte1 & 0x7c) >> 2) + ((((byte1 & 0x03) << 8) | byte2) * 0.001)
    if byte1 & 0x80 != 0:
        value = value * -1
    return value


def pack_string(value, length):
    if isinstance(value, str):
        value = value.encode()
    value = BitArray(value)
    assert value.length == to_bit(length)
    return value.bytes


def unpack_string(buffer, offset, length):
    if length is None:
        length = len(buffer)
    return buffer[offset:offset+length].decode()


def pack_byte(value, length):
    value = BitArray(value)
    assert value.length == to_bit(length)
    return value.bytes


def unpack_byte(buffer, offset, length):
    if length is None:
        length = len(buffer)
    return bytes(buffer[offset:offset+length])


formatpack = {
    'int': pack_signed_int,
    'uint': pack_unsigned_int,
    'hex': pack_hex_string,
    'epoch': pack_time_epoch,
    'float': pack_float,

    'float_2': pack_float_format6,
    'float_3': pack_float_format8,

    'str': pack_string,
    'byte': pack_byte
}


formatunpack = {
    'int': unpack_signed_int,
    'uint': unpack_unsigned_int,
    'hex': unpack_hex_string,
    'epoch': unpack_time_epoch,
    'float': unpack_float,

    'float_2': unpack_float_format6,
    'float_3': unpack_float_format8,

    'str': unpack_string,
    'byte': unpack_byte
}


def to_byte(value):
    return ceil(value / 8)


def to_bit(value):
    return int(value * 8)


def waggle_pack_into(format, length, values):
    logger.debug('pack_into %s %s %s', format, length, values)

    for f, l, v in zip(format, length, values):
        yield formatpack[f](v, l)


def waggle_unpack_from(format, length, buffer):
    offset = 0
    for f, l in zip(format, length):
        value = formatunpack[f](buffer, offset, l)
        yield value

        # for variable length values, increment by unpacked length
        if l is None:
            offset += len(value)
        else:
            offset += l

# =================================================
# Waggle protocol v 0.5
# =================================================


def waggle_pack(format, length, values):
    assert len(format) == len(values)
    assert len(format) == len(length)
    logger.debug('pack %s %s %s', format, length, values)
    return b''.join(waggle_pack_into(format, length, values))


def waggle_unpack(format, length, buffer):
    return list(waggle_unpack_from(format, length, buffer))
