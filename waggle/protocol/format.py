'''
Library for working with coresense data formats.

Example

>>> import format

>>> data = format.waggle_pack('1122', [1, 1, 2, 2], [32, 55, -123, -321])
>>> print(format.unpack(data))

Format Reference

- a: signed integer
- b: unsigned integer
- c: hex string
- d: time epoch
- e: float

'''

from math import ceil
import struct

from bitstring import BitArray


def pack_unsigned_int(value, length):
    assert value >= 0
    length_in_bit = to_bit(length)
    assert value < pow(2, length_in_bit)

    return BitArray(length=length_in_bit, uint=value).bin

def unpack_unsigned_int(buffer, offset, length):
    value = 0

    for i in range(0, length):
        value <<= 8
        value |= buffer[offset + i]

    return value

def pack_signed_int(value, buffer, offset, length):
    pack_unsigned_int_into(abs(value), buffer, offset, length)

    if value < 0:
        buffer[offset + 0] |= 0x80
    else:
        buffer[offset + 0] &= 0x7F


def unpack_signed_int(buffer, offset, length):
    value = buffer[offset + 0] & 0x7F

    for i in range(1, length):
        value <<= 8
        value |= buffer[offset + i]

    if buffer[offset + 0] & 0x80 != 0:
        value = -value

    return value

def pack_float(value, buffer, offset, length):
    assert -127.99 <= value <= 127.99

    absvalue = abs(value)
    intpart = int(absvalue)
    fracpart = int(100 * (absvalue - intpart))

    buffer[offset + 0] = intpart & 0x7F
    buffer[offset + 1] = fracpart & 0x7F

    if value < 0:
        buffer[offset + 0] |= 0x80


def unpack_float(buffer, offset):
    byte1 = buffer[offset + 0]
    byte2 = buffer[offset + 1]
    # have to be careful here, we do not want three decimal placed here.
    value = (byte1 & 0x7F) + (((byte2 & 0x7F) % 100) * 0.01)
    if (byte1 & 0x80) == 0x80:
        value = value * -1
    return value


def pack_hex_string(macaddr, buffer, offset):
    assert len(macaddr) == 12

    for i in range(0, 6):
        buffer[offset + i] = int(macaddr[2*i:2*i+2], 16)


def unpack_hex_string(buffer, offset):
    return ''.join(map(format_hex, (buffer[offset + i] for i in range(6))))


def pack_time_epoch(macaddr, buffer, offset):
    assert len(macaddr) == 12

    for i in range(0, 6):
        buffer[offset + i] = int(macaddr[2*i:2*i+2], 16)


def unpack_time_epoch(buffer, offset):
    return ''.join(map(format_hex, (buffer[offset + i] for i in range(6))))


formatpack = {
    'a': pack_signed_int,
    'b': pack_unsigned_int,
    'c': pack_hex_string,
    'd': pack_time_epoch,
    'e': pack_float,
}


formatunpack = {
    'a': unpack_signed_int,
    'b': unpack_unsigned_int,
    'c': unpack_hex_string,
    'd': unpack_time_epoch,
    'e': unpack_float,
}

def to_byte(value):
    return ceil(value / 8)

def to_bit(value):
    return int(value * 8)


def unpack_from(format, buffer, offset=0):
    # This helps with compatibility between Python 2 and 3 in terms
    # of how values in an array are accessed.
    if not isinstance(buffer, bytearray):
        buffer = bytearray(buffer)

    values = []

    for f in format:
        values.append(formatunpack[f](buffer, offset))
        offset += formatsize[f]

    return tuple(values)


def unpack(format, buffer):
    assert calcsize(format) == len(buffer)
    return unpack_from(format, buffer, offset=0)

def waggle_pack_into(format, length, values):
    for f, l, v in zip(format, length, values):
        yield formatpack[f](v, l)

# =================================================
# Waggle protocol v 0.5
# =================================================
def waggle_pack(format, length, values):
    assert len(format) == len(values)
    assert len(format) == len(length)

    packed_values_in_bit = ''.join(waggle_pack_into(format, length, values))
    return BitArray(bin=packed_values_in_bit).tobytes()


