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
import array


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


def crc8(data, value):
    for x in data:
        value = crc8_table[value ^ x]
    return value


class CRCReader:

    def __init__(self, reader, func):
        self.reader = reader
        self.func = func
        self.sum = 0

    def read(self, n):
        s = self.reader.read(n)
        self.sum = self.func(s, self.sum)
        return s


class CRCWriter:

    def __init__(self, writer, func):
        self.writer = writer
        self.func = func
        self.sum = 0

    def write(self, s):
        self.writer.write(s)
        self.sum = self.func(s, self.sum)


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

    def encode_sensorgram(self, sg):
        body = encode_values(sg['value'])

        crcw = CRCWriter(self.writer, crc8)
        e = BasicEncoder(crcw)
        e.encode_uint(len(body), 2)
        e.encode_uint(get_timestamp_or_now(sg), 4)
        e.encode_uint(sg['id'], 2)
        e.encode_uint(sg.get('inst', 0), 1)
        e.encode_uint(sg['sub_id'], 1)
        e.encode_uint(sg.get('source_id', 0), 2)
        e.encode_uint(sg.get('source_inst', 0), 1)
        e.encode_bytes(body)
        e.encode_uint(crcw.sum, 1)
        assert crcw.sum == 0

    def encode_datagram(self, value):
        crcw = CRCWriter(self.writer, crc16)
        e = BasicEncoder(crcw)
        e.encode_uint(len(value['body']), 3)
        e.encode_uint(value.get('protocol_version', PROTOCOL_MAJOR_VERSION), 1)
        e.encode_uint(get_timestamp_or_now(value), 4)
        e.encode_uint(value.get('packet_seq', get_packet_sequence_number()), 2)
        e.encode_uint(value.get('packet_type', 0), 1)
        e.encode_uint(value.get('plugin_id', 0), 2)
        e.encode_uint(value.get('plugin_major_version', 0), 1)
        e.encode_uint(value.get('plugin_minor_version', 0), 1)
        e.encode_uint(value.get('plugin_patch_version', 0), 1)
        e.encode_uint(value.get('plugin_instance', 0), 1)
        e.encode_uint(value.get('plugin_run_id', RUN_ID), 2)
        e.encode_bytes(value['body'])
        e.encode_uint(crcw.sum, 2)
        assert crcw.sum == 0

    def encode_message_header(self, value):
        protocol_major_version = value.get(
            'protocol_major_version', PROTOCOL_MAJOR_VERSION)
        protocol_minor_version = value.get(
            'protocol_major_version', PROTOCOL_MINOR_VERSION)
        protocol_patch_version = value.get(
            'protocol_major_version', PROTOCOL_PATCH_VERSION)
        message_priority = value.get('message_priority', 0)

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

        crcw = CRCWriter(self.writer, crc16)
        e = BasicEncoder(crcw)
        e.encode_uint(protocol_major_version, 1)
        e.encode_uint(protocol_minor_version, 1)
        e.encode_uint(protocol_patch_version, 1)
        e.encode_uint(message_priority, 1)
        e.encode_uint(len(value['body']), 4)
        e.encode_uint(get_timestamp_or_now(value), 4)
        e.encode_uint(value.get('message_major_type', 0), 1)
        e.encode_uint(value.get('message_minor_type', 0), 1)
        e.encode_uint(0, 2)  # reserved
        e.encode_bytes(sender_id)
        e.encode_bytes(sender_sub_id)
        e.encode_bytes(receiver_id)
        e.encode_bytes(receiver_sub_id)
        e.encode_uint(value.get('sender_seq', get_sender_sequence_number()), 3)
        e.encode_uint(value.get('sender_sid', 0), 2)
        e.encode_uint(value.get('response_seq', 0), 3)
        e.encode_uint(value.get('response_sid', 0), 2)
        e.encode_uint(crcw.sum, 2)
        assert crcw.sum == 0

    def encode_message_token(self, value):
        e = BasicEncoder(self.writer)
        e.encode_uint(value.get('token', 0), 4)

    def encode_message_content(self, value):
        crcw = CRCWriter(self.writer, crc32)
        e = BasicEncoder(crcw)
        e.encode_bytes(value['body'])
        e.encode_uint(crcw.sum, 4)
        assert crcw.sum == 0

    def encode_waggle_packet(self, value):
        self.encode_message_header(value)
        self.encode_message_token(value)
        self.encode_message_content(value)


class Decoder:

    def __init__(self, reader):
        self.reader = reader

    def decode_sensorgram(self):
        r = {}

        crcr = CRCReader(self.reader, crc8)
        d = BasicDecoder(crcr)
        r['body_length'] = d.decode_uint(2)
        r['timestamp'] = d.decode_uint(4)
        r['id'] = d.decode_uint(2)
        r['inst'] = d.decode_uint(1)
        r['sub_id'] = d.decode_uint(1)
        r['source_id'] = d.decode_uint(2)
        r['source_inst'] = d.decode_uint(1)
        r['value'] = decode_values(d.decode_bytes(r['body_length']))
        r['crc'] = d.decode_uint(1)

        if crcr.sum != 0:
            raise ValueError('incorrect sensorgram crc')

        return r

    def decode_datagram(self):
        r = {}

        crcr = CRCReader(self.reader, crc16)
        d = BasicDecoder(crcr)
        r['body_length'] = d.decode_uint(3)
        r['protocol_version'] = d.decode_uint(1)
        r['timestamp'] = d.decode_uint(4)
        r['packet_seq'] = d.decode_uint(2)
        r['packet_type'] = d.decode_uint(1)
        r['plugin_id'] = d.decode_uint(2)
        r['plugin_major_version'] = d.decode_uint(1)
        r['plugin_minor_version'] = d.decode_uint(1)
        r['plugin_patch_version'] = d.decode_uint(1)
        r['plugin_instance'] = d.decode_uint(1)
        r['plugin_run_id'] = d.decode_uint(2)
        r['body'] = d.decode_bytes(r['body_length'])
        r['crc'] = d.decode_uint(2)

        if crcr.sum != 0:
            raise ValueError('invalid datagram crc')

        return r

    def decode_message_header(self, r):
        crcr = CRCReader(self.reader, crc16)
        d = BasicDecoder(crcr)
        r['protocol_major_version'] = d.decode_uint(1)
        r['protocol_minor_version'] = d.decode_uint(1)
        r['protocol_patch_version'] = d.decode_uint(1)
        r['message_priority'] = d.decode_uint(1)
        r['body_length'] = d.decode_uint(4)
        r['timestamp'] = d.decode_uint(4)
        r['message_major_type'] = d.decode_uint(1)
        r['message_minor_type'] = d.decode_uint(1)
        r['reserved'] = d.decode_uint(2)
        r['sender_id'] = d.decode_bytes(8).hex()
        r['sender_sub_id'] = d.decode_bytes(8).hex()
        r['receiver_id'] = d.decode_bytes(8).hex()
        r['receiver_sub_id'] = d.decode_bytes(8).hex()
        r['sender_seq'] = d.decode_uint(3)
        r['sender_sid'] = d.decode_uint(2)
        r['response_seq'] = d.decode_uint(3)
        r['response_sid'] = d.decode_uint(2)
        r['header_crc'] = d.decode_uint(2)

        if crcr.sum != 0:
            raise ValueError('invalid message header crc')

    def decode_message_token(self, r):
        d = BasicDecoder(self.reader)
        r['token'] = d.decode_uint(4)

    def decode_message_content(self, r):
        crcr = CRCReader(self.reader, crc32)
        d = BasicDecoder(crcr)
        r['body'] = d.decode_bytes(r['body_length'])
        r['body_crc'] = d.decode_uint(4)

        if crcr.sum != 0:
            raise ValueError('invalid message body crc')

    def decode_waggle_packet(self):
        r = {}
        self.decode_message_header(r)
        self.decode_message_token(r)
        self.decode_message_content(r)
        return r


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

# TODO varint would also be interesting for uint array types. it would allows us
# to handle a "list of integers" in a uniform way.


def encode_byte_array(e, x):
    e.encode_uint(len(x), 2)
    e.encode_bytes(x)


def encode_string(e, x):
    encode_byte_array(e, x.encode())


def encode_uint_array(e, intsize, values):
    e.encode_uint(len(values), 2)
    for x in values:
        e.encode_uint(x, intsize)


def decode_byte_array(d):
    count = d.decode_uint(2)
    return d.decode_bytes(count)


def decode_string(d):
    return decode_byte_array(d).decode()


def decode_uint_array(d, intsize):
    count = d.decode_uint(2)
    return [d.decode_uint(intsize) for _ in range(count)]


encode_values_table = {
    TYPE_UINT8: lambda e, x: e.encode_uint(x, 1),
    TYPE_UINT16: lambda e, x: e.encode_uint(x, 2),
    TYPE_UINT24: lambda e, x: e.encode_uint(x, 3),
    TYPE_UINT32: lambda e, x: e.encode_uint(x, 4),

    TYPE_BYTE_ARRAY: lambda e, x: encode_byte_array(e, x),
    TYPE_STRING: lambda e, x: encode_string(e, x),
    TYPE_UINT8_ARRAY: lambda e, x: encode_uint_array(e, 1, x),
    TYPE_UINT16_ARRAY: lambda e, x: encode_uint_array(e, 2, x),
    TYPE_UINT24_ARRAY: lambda e, x: encode_uint_array(e, 3, x),
    TYPE_UINT32_ARRAY: lambda e, x: encode_uint_array(e, 4, x),
}


def detect_value_type(x):
    if isinstance(x, (bytes, bytearray)):
        return TYPE_BYTE_ARRAY
    if isinstance(x, str):
        return TYPE_STRING
    if isinstance(x, int) and x >= 0:
        if x <= 0xff:
            return TYPE_UINT8
        if x <= 0xffff:
            return TYPE_UINT16
        if x <= 0xffffff:
            return TYPE_UINT24
        if x <= 0xffffffff:
            return TYPE_UINT32
        raise ValueError('uint too large')
    if isinstance(x, (list, tuple)):
        # should do more uniform checking or have type escalation
        return max(map(detect_value_type, x)) | 0x80


def encode_values(values):
    w = BytesIO()
    e = BasicEncoder(w)

    if not isinstance(values, (list, tuple)):
        values = [values]

    for x in values:
        value_type = detect_value_type(x)
        e.encode_uint(value_type, 1)
        encode_values_table[value_type](e, x)

    return w.getvalue()


decode_values_table = {
    TYPE_UINT8: lambda d: d.decode_uint(1),
    TYPE_UINT16: lambda d: d.decode_uint(2),
    TYPE_UINT24: lambda d: d.decode_uint(3),
    TYPE_UINT32: lambda d: d.decode_uint(4),

    TYPE_BYTE_ARRAY: lambda d: decode_byte_array(d),
    TYPE_STRING: lambda d: decode_string(d),
    TYPE_UINT8_ARRAY: lambda d: decode_uint_array(d, 1),
    TYPE_UINT16_ARRAY: lambda d: decode_uint_array(d, 2),
    TYPE_UINT24_ARRAY: lambda d: decode_uint_array(d, 3),
    TYPE_UINT32_ARRAY: lambda d: decode_uint_array(d, 4),
}


def decode_next_value(r):
    d = BasicDecoder(r)
    value_type = d.decode_uint(1)
    return decode_values_table[value_type](d)


def decode_values(data):
    results = []

    reader = BytesIO(data)

    while True:
        try:
            results.append(decode_next_value(reader))
        except EOFError:
            break

    # ugly... we probably shouldn't do this
    if len(results) == 1:
        return results[0]
    else:
        return tuple(results)


if __name__ == '__main__':
    from serial import Serial
    from base64 import b64encode, b64decode
    import binascii
    import sys

    with Serial(sys.argv[1], 9600, timeout=3) as ser:
        while True:
            sg = {
                'timestamp': int(time.time()),
                'id': 2222,
                'inst': 33,
                'sub_id': 44,
                'source_id': 5555,
                'source_inst': 66,
                'value': [7, 88, 9999],
            }
            encoded = b64encode(pack_sensorgram(sg))

            print('>>> sending test sensorgram')
            print(sg)
            print(encoded.decode())
            ser.write(encoded)
            ser.write(b'\n')
            print()

            print('>>> printing output')

            while True:
                line = ser.readline()
                if len(line) == 0:
                    break
                print(line.strip().decode())

                try:
                    data = b64decode(line.strip())
                    sg = unpack_sensorgram(data)
                    print('sensorgram from device')
                    print(sg)
                except (binascii.Error, IndexError):
                    pass

            print()
