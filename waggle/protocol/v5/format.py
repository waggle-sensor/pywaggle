'''
Library for working with coresense data formats.

Example

>>> import format

>>> data = format.waggle_pack('abcd', [1, 1, 2, 4], [-32, 55, 'abcd', 1506703931])
>>> print([e for e in format.waggle_unpack('abcd', [1, 1, 2, 4], data)])

Format Reference

- a: signed integer
- b: unsigned integer
- c: hex string
- d: time epoch
- e: float

- f: fixed point (-127.99, 127.99)
- g: fixed point (-31.999, 31.999)

- h: string
- i: byte
'''

from math import ceil
import struct

from bitstring import BitArray


def pack_unsigned_int(value, length):
    length_in_bit = to_bit(length)
    assert 0 <= value < pow(2, length_in_bit)

    return BitArray(uint=value, length=length_in_bit).bin


def unpack_unsigned_int(buffer, offset, length):
    value = BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset))
    return value.uint


def pack_signed_int(value, length):
    length_in_bit = to_bit(length)
    assert -1 * pow(2, length_in_bit - 1) <= value < pow(2, length_in_bit - 1)

    return BitArray(int=value, length=length_in_bit).bin    


def unpack_signed_int(buffer, offset, length):
    value = BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset))
    return value.int


def pack_float(value, length):
    assert int(length) == 4 or int(length) == 8
    assert isinstance(value, float)

    return BitArray(float=value, length=to_bit(length)).bin


def unpack_float(buffer, offset, length):
    value = BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset))
    return value.float


def pack_hex_string(value, length):
    value = BitArray(hex=value)
    assert value.length == to_bit(length)
    return value.bin


def unpack_hex_string(buffer, offset, length):
    value = BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset))
    return value.hex


def pack_time_epoch(value, length):
    return pack_unsigned_int(value, length)


def unpack_time_epoch(buffer, offset, length):
    return unpack_unsigned_int(buffer, offset, length)


def pack_float_format6(value, length=2.0):
    assert -127.99 <= value <= 127.99

    absvalue = abs(value)
    intpart = int(absvalue)
    fracpart = int(100 * round(absvalue - intpart, 2))
    packed = ((intpart & 0x7F) << 8) | fracpart & 0x7F
    if value < 0:
        packed |= 0x8000

    return BitArray(uint=packed, length=to_bit(length)).bin


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

    packed = (((intpart & 0b00011111) << 2) | ((fracpart >> 8) & 0b00000011)) << 8
    packed |= fracpart & 0xFF
    
    if value < 0:
        packed |= 0x80
    return BitArray(uint=packed, length=to_bit(length)).bin


def unpack_float_format8(buffer, offset, length=2.0):
    byte1 = buffer[offset + 0]
    byte2 = buffer[offset + 1]
    value = ((byte1 & 0x7c) >> 2) + ((((byte1 & 0x03) << 8) | byte2) * 0.001)
    if byte1 & 0x80 != 0:
        value = value * -1
    return value

def unpack_string(value, offset, length):
    return value.decode("utf-8")

def unpack_byte(value, offset, length):
    return value.strip()

formatpack = {
    'a': pack_signed_int,
    'b': pack_unsigned_int,
    'c': pack_hex_string,
    'd': pack_time_epoch,
    'e': pack_float,

    'f': pack_float_format6,
    'g': pack_float_format8,
}


formatunpack = {
    'a': unpack_signed_int,
    'b': unpack_unsigned_int,
    'c': unpack_hex_string,
    'd': unpack_time_epoch,
    'e': unpack_float,

    'f': unpack_float_format6,
    'g': unpack_float_format8,

    'h': unpack_string,
    'i': unpack_byte
}


def to_byte(value):
    return ceil(value / 8)


def to_bit(value):
    return int(value * 8)


def waggle_pack_into(format, length, values):
    for f, l, v in zip(format, length, values):
        yield formatpack[f](v, l)


def waggle_unpack_from(format, length, buffer):
    offset = 0
    for f, l in zip(format, length):
        if l == 0:
            yield None
        else:
            yield formatunpack[f](buffer, offset, l)
        offset += l

# =================================================
# Waggle protocol v 0.5
# =================================================
def waggle_pack(format, length, values):
    assert len(format) == len(values)
    assert len(format) == len(length)

    packed_values_in_bit = ''.join(waggle_pack_into(format, length, values))
    return BitArray(bin=packed_values_in_bit).tobytes()


def waggle_unpack(format, length, buffer):
    return waggle_unpack_from(format, length, buffer)


