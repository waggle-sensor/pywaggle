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

from math import ceil
from bitstring import BitArray
from binascii import hexlify


# NOTE It seems that bitstring's is much slower than more direct methods. I've
# implemented optimized versions for some of the unpack functions, since they're
# used to do bulk decoding. - Sean


def pack_unsigned_int(value, length):
    length_in_bit = to_bit(length)
    assert 0 <= value < pow(2, length_in_bit)

    return BitArray(uint=value, length=length_in_bit).bin


def unpack_unsigned_int(buffer, offset, length):
    return BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset)).uint

    if length == 1:
        value = buffer[offset]
    elif length == 2:
        value = (buffer[offset]<<8) | buffer[offset+1]
    elif length == 3:
        value = (buffer[offset]<<16) | (buffer[offset+1]<<8) | buffer[offset+2]
    elif length == 4:
        value = (buffer[offset]<<24) | (buffer[offset+1]<<16) | (buffer[offset+2]<<8) | buffer[offset+3]
    else:
        raise ValueError('Invalid length.')

    return value


def pack_signed_int(value, length):
    length_in_bit = to_bit(length)
    assert -1 * pow(2, length_in_bit - 1) <= value < pow(2, length_in_bit - 1)

    return BitArray(int=value, length=length_in_bit).bin


def unpack_signed_int(buffer, offset, length):
    return BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset)).int

    if length == 1:
        value = buffer[offset]&0x7F
    elif length == 2:
        value = ((buffer[offset]&0x7F)<<8) | buffer[offset+1]
    elif length == 3:
        value = ((buffer[offset]&0x7F)<<16) | (buffer[offset+1]<<8) | buffer[offset+2]
    elif length == 4:
        value = ((buffer[offset]&0x7F)<<24) | (buffer[offset+1]<<16) | (buffer[offset+2]<<8) | buffer[offset+3]
    else:
        raise ValueError('Invalid length.')

    if buffer[offset]&0x80 == 0:
        return value
    else:
        return -value


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
    return hexlify(buffer[offset:offset+length]).decode()


def pack_time_epoch(value, length):
    return pack_unsigned_int(value, length)


unpack_time_epoch = unpack_unsigned_int


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


def pack_string(value, length):
    if isinstance(value, str):
        value = value.encode()
    value = BitArray(value)
    assert value.length == to_bit(length)
    return value.bin


def unpack_string(buffer, offset, length):
    if length is None:
        length = len(buffer)
    # return buffer[offset:offset+length].decode()
    value = BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset))
    return value.tobytes().decode()


def pack_byte(value, length):
    value = BitArray(value)
    assert value.length == to_bit(length)
    return value.bin


def unpack_byte(buffer, offset, length):
    if length is None:
        length = len(buffer)
    # return bytes(buffer[offset:offset+length])
    value = BitArray(bytes=buffer, length=to_bit(length), offset=to_bit(offset))
    return value.tobytes()


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

    packed_values_in_bit = ''.join(waggle_pack_into(format, length, values))
    return BitArray(bin=packed_values_in_bit).tobytes()


def waggle_unpack(format, length, buffer):
    return waggle_unpack_from(format, length, buffer)
