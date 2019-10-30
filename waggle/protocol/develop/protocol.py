# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import time
from io import BytesIO
from binascii import crc_hqx
from binascii import crc32
import random
import struct
import logging


logger = logging.getLogger('waggle.protocol')


crc8_table = [
    0x00, 0x5e, 0xbc, 0xe2, 0x61, 0x3f, 0xdd, 0x83,
    0xc2, 0x9c, 0x7e, 0x20, 0xa3, 0xfd, 0x1f, 0x41,
    0x9d, 0xc3, 0x21, 0x7f, 0xfc, 0xa2, 0x40, 0x1e,
    0x5f, 0x01, 0xe3, 0xbd, 0x3e, 0x60, 0x82, 0xdc,
    0x23, 0x7d, 0x9f, 0xc1, 0x42, 0x1c, 0xfe, 0xa0,
    0xe1, 0xbf, 0x5d, 0x03, 0x80, 0xde, 0x3c, 0x62,
    0xbe, 0xe0, 0x02, 0x5c, 0xdf, 0x81, 0x63, 0x3d,
    0x7c, 0x22, 0xc0, 0x9e, 0x1d, 0x43, 0xa1, 0xff,
    0x46, 0x18, 0xfa, 0xa4, 0x27, 0x79, 0x9b, 0xc5,
    0x84, 0xda, 0x38, 0x66, 0xe5, 0xbb, 0x59, 0x07,
    0xdb, 0x85, 0x67, 0x39, 0xba, 0xe4, 0x06, 0x58,
    0x19, 0x47, 0xa5, 0xfb, 0x78, 0x26, 0xc4, 0x9a,
    0x65, 0x3b, 0xd9, 0x87, 0x04, 0x5a, 0xb8, 0xe6,
    0xa7, 0xf9, 0x1b, 0x45, 0xc6, 0x98, 0x7a, 0x24,
    0xf8, 0xa6, 0x44, 0x1a, 0x99, 0xc7, 0x25, 0x7b,
    0x3a, 0x64, 0x86, 0xd8, 0x5b, 0x05, 0xe7, 0xb9,
    0x8c, 0xd2, 0x30, 0x6e, 0xed, 0xb3, 0x51, 0x0f,
    0x4e, 0x10, 0xf2, 0xac, 0x2f, 0x71, 0x93, 0xcd,
    0x11, 0x4f, 0xad, 0xf3, 0x70, 0x2e, 0xcc, 0x92,
    0xd3, 0x8d, 0x6f, 0x31, 0xb2, 0xec, 0x0e, 0x50,
    0xaf, 0xf1, 0x13, 0x4d, 0xce, 0x90, 0x72, 0x2c,
    0x6d, 0x33, 0xd1, 0x8f, 0x0c, 0x52, 0xb0, 0xee,
    0x32, 0x6c, 0x8e, 0xd0, 0x53, 0x0d, 0xef, 0xb1,
    0xf0, 0xae, 0x4c, 0x12, 0x91, 0xcf, 0x2d, 0x73,
    0xca, 0x94, 0x76, 0x28, 0xab, 0xf5, 0x17, 0x49,
    0x08, 0x56, 0xb4, 0xea, 0x69, 0x37, 0xd5, 0x8b,
    0x57, 0x09, 0xeb, 0xb5, 0x36, 0x68, 0x8a, 0xd4,
    0x95, 0xcb, 0x29, 0x77, 0xf4, 0xaa, 0x48, 0x16,
    0xe9, 0xb7, 0x55, 0x0b, 0x88, 0xd6, 0x34, 0x6a,
    0x2b, 0x75, 0x97, 0xc9, 0x4a, 0x14, 0xf6, 0xa8,
    0x74, 0x2a, 0xc8, 0x96, 0x15, 0x4b, 0xa9, 0xf7,
    0xb6, 0xe8, 0x0a, 0x54, 0xd7, 0x89, 0x6b, 0x35,
]


def update_crc(sum, table, data):
    for value in data:
        sum = table[sum ^ value]
    return sum


def crc8(data):
    return update_crc(0, crc8_table, data)


class CRC8Writer:

    def __init__(self, w):
        self.w = w
        self.sum = 0

    def write(self, s):
        self.w.write(s)
        self.sum = update_crc(self.sum, crc8_table, s)


class CRC8Reader:

    def __init__(self, r):
        self.r = r
        self.sum = 0

    def read(self, n):
        s = self.r.read(n)
        self.sum = update_crc(self.sum, crc8_table, s)
        return s


class BasicEncoder:

    def __init__(self, w):
        self.w = w

    def encode_bytes(self, b):
        self.w.write(b)

    def encode_uint(self, x, n):
        self.encode_bytes(x.to_bytes(n, byteorder='big'))


class BasicDecoder:

    def __init__(self, r):
        self.r = r

    def decode_bytes(self, n):
        data = self.r.read(n)
        if len(data) != n:
            raise EOFError()
        return data

    def decode_uint(self, size):
        return int.from_bytes(self.decode_bytes(size), byteorder='big')


RUN_ID = random.randint(0, 0xffff - 1)

PROTOCOL_MAJOR_VERSION = 2
PROTOCOL_MINOR_VERSION = 1
PROTOCOL_PATCH_VERSION = 0

sender_sequence = 0
packet_sequence = 0


def get_sender_sequence_number():
    global sender_sequence
    result = sender_sequence
    sender_sequence = (sender_sequence + 1) & 0xffff
    return result


def get_packet_sequence_number():
    global packet_sequence
    result = packet_sequence
    packet_sequence = (packet_sequence + 1) & 0xffff
    return result


def crc16(data, value=0):
    return crc_hqx(data, value)


def get_timestamp_or_now(obj):
    return obj.get('timestamp') or int(time.time())


def assert_length(b, length):
    if len(b) != 8:
        raise ValueError('len({}) != {}'.format(b, length))


class Encoder:

    def __init__(self, writer):
        self.writer = writer

    def encode_bytes(self, value):
        logger.debug('encode_bytes %r', value)
        length = self.writer.write(value)

        if length != len(value):
            raise IOError('Failed to encode bytes.')

    def encode_string(self, s):
        self.encode_bytes(s.encode())

    def encode_uint(self, length, value):
        self.encode_bytes(value.to_bytes(length, 'big'))

    def encode_int(self, length, value):
        self.encode_bytes(value.to_bytes(length, 'big', signed=True))

    def encode_float(self, x):
        self.encode_bytes(struct.pack('f', x))

    def encode_sensorgram(self, sg):
        body = pack_typed_values(sg['value'])
        self.encode_uint(2, len(body))
        self.encode_uint(2, sg['sensor_id'])
        self.encode_uint(1, sg.get('sensor_instance', 0))
        self.encode_uint(1, sg['parameter_id'])
        self.encode_uint(4, get_timestamp_or_now(sg))
        self.encode_bytes(body)

    def encode_datagram(self, value):
        protocol_version = value.get(
            'protocol_version', PROTOCOL_MAJOR_VERSION)
        timestamp = get_timestamp_or_now(value)
        packet_seq = value.get('packet_seq', get_packet_sequence_number())
        packet_type = value.get('packet_type', 0)
        plugin_id = value.get('plugin_id', 0)
        plugin_major_version = value.get('plugin_major_version', 0)
        plugin_minor_version = value.get('plugin_minor_version', 0)
        plugin_patch_version = value.get('plugin_patch_version', 0)
        plugin_instance = value.get('plugin_instance', 0)
        plugin_run_id = value.get('plugin_run_id', RUN_ID)
        body = value['body']
        body_length = len(body)
        body_crc = crc8(body)

        self.encode_uint(3, body_length)
        self.encode_uint(1, protocol_version)
        self.encode_uint(4, timestamp)
        self.encode_uint(2, packet_seq)
        self.encode_uint(1, packet_type)
        self.encode_uint(2, plugin_id)
        self.encode_uint(1, plugin_major_version)
        self.encode_uint(1, plugin_minor_version)
        self.encode_uint(1, plugin_patch_version)
        self.encode_uint(1, plugin_instance)
        self.encode_uint(2, plugin_run_id)
        self.encode_bytes(body)
        self.encode_uint(1, body_crc)

    def encode_waggle_packet_header(self, value):
        protocol_major_version = value.get(
            'protocol_major_version', PROTOCOL_MAJOR_VERSION)
        protocol_minor_version = value.get(
            'protocol_major_version', PROTOCOL_MINOR_VERSION)
        protocol_patch_version = value.get(
            'protocol_major_version', PROTOCOL_PATCH_VERSION)
        message_priority = value.get('message_priority', 0)
        body = value['body']
        body_length = len(body)
        timestamp = get_timestamp_or_now(value)
        message_major_type = value.get('message_major_type', 0)
        message_minor_type = value.get('message_minor_type', 0)
        reserved = 0

        sender_id = bytes.fromhex(value.get('sender_id', '0000000000000000'))
        assert_length(sender_id, 8)

        sender_sub_id = bytes.fromhex(
            value.get('sender_sub_id', '0000000000000000'))
        assert_length(sender_sub_id, 8)

        receiver_id = bytes.fromhex(
            value.get('receiver_id', '0000000000000000'))
        assert_length(receiver_id, 8)

        receiver_sub_id = bytes.fromhex(
            value.get('receiver_sub_id', '0000000000000000'))
        assert_length(receiver_sub_id, 8)

        sender_seq = value.get('sender_seq', get_sender_sequence_number())
        sender_sid = value.get('sender_sid', 0)
        response_seq = value.get('response_seq', 0)
        response_sid = value.get('response_sid', 0)

        self.encode_uint(1, protocol_major_version)
        self.encode_uint(1, protocol_minor_version)
        self.encode_uint(1, protocol_patch_version)
        self.encode_uint(1, message_priority)
        self.encode_uint(4, body_length)
        self.encode_uint(4, timestamp)
        self.encode_uint(1, message_major_type)
        self.encode_uint(1, message_minor_type)
        self.encode_uint(2, reserved)
        self.encode_bytes(sender_id)
        self.encode_bytes(sender_sub_id)
        self.encode_bytes(receiver_id)
        self.encode_bytes(receiver_sub_id)
        self.encode_uint(3, sender_seq)
        self.encode_uint(2, sender_sid)
        self.encode_uint(3, response_seq)
        self.encode_uint(2, response_sid)

    def encode_waggle_packet(self, value):
        buf = BytesIO()
        enc = Encoder(buf)
        enc.encode_waggle_packet_header(value)
        header = buf.getvalue()

        header_crc = crc16(header)
        token = value.get('token', 0)
        body = value['body']
        body_crc = crc32(value['body'])

        self.encode_bytes(header)
        self.encode_uint(2, header_crc)
        self.encode_uint(4, token)
        self.encode_bytes(body)
        self.encode_uint(4, body_crc)


class Decoder:

    def __init__(self, reader):
        self.reader = reader

    def decode_bytes(self, length):
        b = self.reader.read(length)

        if len(b) != length:
            raise EOFError()

        return b

    def decode_string(self, length):
        return self.decode_bytes(length).decode()

    def decode_uint(self, length):
        return int.from_bytes(self.decode_bytes(length), 'big')

    def decode_int(self, length):
        return int.from_bytes(self.decode_bytes(length), 'big', signed=True)

    def decode_float(self):
        return struct.unpack('f', self.decode_bytes(4))[0]

    def decode_bytes_value(self):
        # add type checks here...
        return self.reader.read()

    def decode_string_value(self):
        # add type checks here...
        return self.reader.read().decode()

    def decode_list_of_floats_value(self):
        b = self.reader.read()
        n = len(b) // 4
        return list(struct.unpack('{}f'.format(n), b))

    def decode_sensorgram(self):
        r = {}

        crcr = CRC8Reader(self.reader)
        d = BasicDecoder(crcr)

        # should we make this the whole length instead?
        body_length = d.decode_uint(2)
        r['timestamp'] = d.decode_uint(4)
        r['id'] = d.decode_uint(2)
        r['inst'] = d.decode_uint(1)
        r['sub_id'] = d.decode_uint(1)
        r['source_id'] = d.decode_uint(2)
        r['source_inst'] = d.decode_uint(1)
        r['value'] = decode_sensorgram_values(d.decode_bytes(body_length))

        # read crc byte to update crc reader sum
        _ = d.decode_uint(1)

        if crcr.sum != 0:
            raise ValueError('incorrect sensorgram crc')

        return r

    def decode_datagram(self):
        start_flag = self.decode_uint(1)

        if start_flag != START_FLAG:
            raise ValueError('Invalid start flag.')

        body_length = self.decode_uint(3)
        protocol_version = self.decode_uint(1)
        timestamp = self.decode_uint(4)
        packet_seq = self.decode_uint(2)
        packet_type = self.decode_uint(1)
        plugin_id = self.decode_uint(2)
        plugin_major_version = self.decode_uint(1)
        plugin_minor_version = self.decode_uint(1)
        plugin_patch_version = self.decode_uint(1)
        plugin_instance = self.decode_uint(1)
        plugin_run_id = self.decode_uint(2)
        body = self.decode_bytes(body_length)
        body_crc = self.decode_uint(1)

        if crc8(body) != body_crc:
            raise ValueError('Invalid body CRC.')

        end_flag = self.decode_uint(1)

        if end_flag != END_FLAG:
            raise ValueError('Invalid end flag.')

        return {
            'timestamp': timestamp,
            'packet_seq': packet_seq,
            'packet_type': packet_type,
            'plugin_id': plugin_id,
            'plugin_major_version': plugin_major_version,
            'plugin_minor_version': plugin_minor_version,
            'plugin_patch_version': plugin_patch_version,
            'plugin_instance': plugin_instance,
            'plugin_run_id': plugin_run_id,
            'body': body,
        }

    def decode_waggle_packet(self):
        header = self.decode_bytes(58)
        header_crc = self.decode_uint(2)

        if crc16(header) != header_crc:
            raise ValueError('Invalid header CRC.')

        dec = Decoder(BytesIO(header))
        protocol_major_version = dec.decode_uint(1)
        protocol_minor_version = dec.decode_uint(1)
        protocol_patch_version = dec.decode_uint(1)
        message_priority = dec.decode_uint(1)
        body_length = dec.decode_uint(4)
        timestamp = dec.decode_uint(4)
        message_major_type = dec.decode_uint(1)
        message_minor_type = dec.decode_uint(1)
        reserved = dec.decode_uint(2)
        sender_id = dec.decode_bytes(8).hex()
        sender_sub_id = dec.decode_bytes(8).hex()
        receiver_id = dec.decode_bytes(8).hex()
        receiver_sub_id = dec.decode_bytes(8).hex()
        sender_seq = dec.decode_uint(3)
        sender_sid = dec.decode_uint(2)
        response_seq = dec.decode_uint(3)
        response_sid = dec.decode_uint(2)

        token = self.decode_uint(4)
        body = self.decode_bytes(body_length)
        body_crc = self.decode_uint(4)

        if crc32(body) != body_crc:
            raise ValueError('Invalid body CRC.')

        return {
            'timestamp': timestamp,
            'protocol_major_version': protocol_major_version,
            'protocol_minor_version': protocol_minor_version,
            'protocol_patch_version': protocol_patch_version,
            'message_priority': message_priority,
            'message_major_type': message_major_type,
            'message_minor_type': message_minor_type,
            'sender_id': sender_id,
            'sender_sub_id': sender_sub_id,
            'sender_seq': sender_seq,
            'sender_sid': sender_sid,
            'receiver_id': receiver_id,
            'receiver_sub_id': receiver_sub_id,
            'response_seq': response_seq,
            'response_sid': response_sid,
            'token': token,
            'body': body,
        }


TYPE_NULL = 0x00
TYPE_BYTE = 0x01
TYPE_CHAR = 0x02
TYPE_INT8 = 0x03
TYPE_UINT8 = 0x04
TYPE_INT16 = 0x05
TYPE_UINT16 = 0x06
TYPE_INT24 = 0x07
TYPE_UINT24 = 0x08
TYPE_INT32 = 0x09
TYPE_UINT32 = 0x0a
TYPE_FLOAT16 = 0x0b
TYPE_FLOAT32 = 0x0c
TYPE_FLOAT64 = 0x0d

# same as scalar types but with high bit set
TYPE_BYTE_ARRAY = 0x81
TYPE_STRING = 0x82
TYPE_INT8_ARRAY = 0x83
TYPE_UINT8_ARRAY = 0x84
TYPE_INT16_ARRAY = 0x85
TYPE_UINT16_ARRAY = 0x86
TYPE_INT24_ARRAY = 0x87
TYPE_UINT24_ARRAY = 0x88
TYPE_INT32_ARRAY = 0x89
TYPE_UINT32_ARRAY = 0x8a
TYPE_FLOAT16_ARRAY = 0x8b
TYPE_FLOAT32_ARRAY = 0x8c
TYPE_FLOAT64_ARRAY = 0x8d


def make_pack_function(func):
    def packer(items):
        buf = BytesIO()
        enc = Encoder(buf)

        for item in items:
            func(enc, item)

        return buf.getvalue()

    return packer


def make_unpack_function(func):
    def unpacker(buf):
        items = []

        dec = Decoder(BytesIO(buf))

        while True:
            try:
                items.append(func(dec))
            except EOFError:
                break

        return items

    return unpacker


pack_sensorgrams = make_pack_function(Encoder.encode_sensorgram)
pack_datagrams = make_pack_function(Encoder.encode_datagram)
pack_waggle_packets = make_pack_function(Encoder.encode_waggle_packet)
pack_messages = pack_waggle_packets

unpack_sensorgrams = make_unpack_function(Decoder.decode_sensorgram)
unpack_datagrams = make_unpack_function(Decoder.decode_datagram)
unpack_waggle_packets = make_unpack_function(Decoder.decode_waggle_packet)
unpack_messages = unpack_waggle_packets


def pack_message(message):
    return pack_waggle_packets([message])


def unpack_message(data):
    return unpack_waggle_packets(data)[0]


def pack_datagram(datagram):
    return pack_datagrams([datagram])


def unpack_datagram(data):
    return unpack_datagrams(data)[0]


def pack_sensorgram(sensorgram):
    return pack_sensorgrams([sensorgram])


def unpack_sensorgram(data):
    return unpack_sensorgrams(data)[0]


def pack_sensor_data_message(sensorgrams):
    if isinstance(sensorgrams, list):
        data = pack_sensorgrams(sensorgrams)
    elif isinstance(sensorgrams, bytes) or isinstance(sensorgrams, bytearray):
        data = sensorgrams
    else:
        raise ValueError('Invalid sensorgram type. Must be list or bytes.')

    return pack_message({
        'receiver_id': '0000000000000000',
        'receiver_sub_id': '0000000000000000',
        'body': pack_datagram({
            'body': data
        })
    })


def decode_uint_array(d, size):
    count = d.decode_uint(2)
    return [d.decode_uint(size) for _ in range(count)]


decode_values_table = {
    TYPE_UINT8: lambda d: d.decode_uint(1),
    TYPE_UINT16: lambda d: d.decode_uint(2),
    TYPE_UINT24: lambda d: d.decode_uint(3),
    TYPE_UINT32: lambda d: d.decode_uint(4),

    TYPE_UINT8_ARRAY: lambda d: decode_uint_array(d, 1),
    TYPE_UINT16_ARRAY: lambda d: decode_uint_array(d, 2),
    TYPE_UINT24_ARRAY: lambda d: decode_uint_array(d, 3),
    TYPE_UINT32_ARRAY: lambda d: decode_uint_array(d, 4),
}


def decode_next_sensorgram_value(r):
    d = BasicDecoder(r)
    value_type = d.decode_uint(1)
    return decode_values_table[value_type](d)


def decode_sensorgram_values(data):
    results = []

    reader = BytesIO(data)

    while True:
        try:
            results.append(decode_next_sensorgram_value(reader))
        except EOFError:
            break

    return tuple(results)


if __name__ == '__main__':
    from base64 import b64decode

    source = BytesIO(
        b'ADERERERIiIzRFVVZgQNBBEGA+mKAAUAAAABAAAAAgAAAAMAAAAEAAAABYoABAAAAAYAAAAHAAAACAAAAAlJ\n')

    while True:
        line = source.readline()
        if len(line) == 0:
            break
        data = b64decode(line.strip())
        print(unpack_sensorgram(data))

    # print(unpack_sensorgram(pack_sensorgram({
    #     'sensor_id': 1,
    #     'parameter_id': 1,
    #     'value': (1, 10.2, 'hello'),
    # })))

    # print(unpack_sensorgram(pack_sensorgram({
    #     'sensor_id': 1,
    #     'parameter_id': 1,
    #     'value': (1, 2, 3, 4, 5, b'more bytes'),
    # })))

    # print(unpack_sensorgram(pack_sensorgram({
    #     'sensor_id': 1,
    #     'parameter_id': 1,
    #     'value': 32.1,
    # })))

    # print(unpack_sensorgram(pack_sensorgram({
    #     'sensor_id': 1,
    #     'parameter_id': 1,
    #     'value': -23,
    # })))

    # print(unpack_sensorgram(pack_sensorgram({
    #     'sensor_id': 1,
    #     'parameter_id': 1,
    #     'value': [1., 2., 3.],
    # })))

    # print(unpack_sensorgram(pack_sensorgram({
    #     'sensor_id': 1,
    #     'parameter_id': 1,
    #     'value': (1, [1., 2., 3.]),
    # })))
