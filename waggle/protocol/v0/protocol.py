# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import time
from io import BytesIO
from waggle.checksum import crc8
from binascii import crc_hqx
from binascii import crc32
import random
import struct
import logging


logger = logging.getLogger('waggle.protocol')


RUN_ID = random.randint(0, 0xffff - 1)

PROTOCOL_MAJOR_VERSION = 2
PROTOCOL_MINOR_VERSION = 1
PROTOCOL_PATCH_VERSION = 0

START_FLAG = 0xaa
END_FLAG = 0x55

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

        self.encode_uint(1, START_FLAG)
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
        self.encode_uint(1, END_FLAG)

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
        body_length = self.decode_uint(2)
        sensor_id = self.decode_uint(2)
        sensor_instance = self.decode_uint(1)
        parameter_id = self.decode_uint(1)
        timestamp = self.decode_uint(4)
        body = self.decode_bytes(body_length)

        return {
            'sensor_id': sensor_id,
            'sensor_instance': sensor_instance,
            'parameter_id': parameter_id,
            'timestamp': timestamp,
            'value': decode_value_type(body),
        }

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
TYPE_BYTES = 0x01
TYPE_STRING = 0x02
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
TYPE_LIST_OF_FLOAT32 = 0x8c


def pack_typed_value(value):
    if isinstance(value, (bytes, bytearray)):
        return TYPE_BYTES, value

    if isinstance(value, str):
        return TYPE_STRING, value.encode()

    if isinstance(value, int):
        if value < 0:
            return packed_type_int_value(value)
        else:
            return packed_type_uint_value(value)

    if isinstance(value, float):
        return TYPE_FLOAT32, struct.pack('f', value)

    if isinstance(value, list) and isinstance(value[0], float):
        return TYPE_LIST_OF_FLOAT32, struct.pack('{}f'.format(len(value)), *value)

    raise ValueError('Unsupported value type.')


def pack_typed_values(value):
    # lift single to tuple
    if not isinstance(value, tuple):
        value = (value,)

    # ensure "expanding" values are the last argument
    for v in value[:-1]:
        if isinstance(v, (bytes, bytearray, str, list)):
            raise TypeError(
                'Value {} of type {} must be last argument'.format(v, type(v)))

    chunks = []

    for v in value:
        t, b = pack_typed_value(v)
        chunks.append(bytes([t]))
        chunks.append(b)

    return b''.join(chunks)


def packed_type_int_value(value):
    try:
        return TYPE_INT8, value.to_bytes(1, byteorder='big', signed=True)
    except OverflowError:
        pass

    try:
        return TYPE_INT16, value.to_bytes(2, byteorder='big', signed=True)
    except OverflowError:
        pass

    try:
        return TYPE_INT24, value.to_bytes(3, byteorder='big', signed=True)
    except OverflowError:
        pass

    try:
        return TYPE_INT32, value.to_bytes(4, byteorder='big', signed=True)
    except OverflowError:
        pass

    raise ValueError('Unsupported int size.')


def packed_type_uint_value(value):
    try:
        return TYPE_UINT8, value.to_bytes(1, byteorder='big', signed=False)
    except OverflowError:
        pass

    try:
        return TYPE_UINT16, value.to_bytes(2, byteorder='big', signed=False)
    except OverflowError:
        pass

    try:
        return TYPE_UINT24, value.to_bytes(3, byteorder='big', signed=False)
    except OverflowError:
        pass

    try:
        return TYPE_UINT32, value.to_bytes(4, byteorder='big', signed=False)
    except OverflowError:
        pass

    raise ValueError('Unsupported unsigned int size.')


decode_value_table = {
    TYPE_BYTES: lambda d: d.decode_bytes_value(),
    TYPE_STRING: lambda d: d.decode_string_value(),

    TYPE_UINT8: lambda d: d.decode_uint(1),
    TYPE_UINT16: lambda d: d.decode_uint(2),
    TYPE_UINT24: lambda d: d.decode_uint(3),
    TYPE_UINT32: lambda d: d.decode_uint(4),

    TYPE_INT8: lambda d: d.decode_int(1),
    TYPE_INT16: lambda d: d.decode_int(2),
    TYPE_INT24: lambda d: d.decode_int(3),
    TYPE_INT32: lambda d: d.decode_int(4),

    TYPE_FLOAT32: lambda d: d.decode_float(),
    TYPE_LIST_OF_FLOAT32: lambda d: d.decode_list_of_floats_value(),
}


def decode_value_type(body):
    results = []

    d = Decoder(BytesIO(body))

    while True:
        try:
            t = d.decode_uint(1)
            results.append(decode_value_table[t](d))
        except EOFError:
            break

    if len(results) == 1:
        return results[0]
    else:
        return tuple(results)


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


if __name__ == '__main__':
    print(unpack_sensorgram(pack_sensorgram({
        'sensor_id': 1,
        'parameter_id': 1,
        'value': (1, 10.2, 'hello'),
    })))

    print(unpack_sensorgram(pack_sensorgram({
        'sensor_id': 1,
        'parameter_id': 1,
        'value': (1, 2, 3, 4, 5, b'more bytes'),
    })))

    print(unpack_sensorgram(pack_sensorgram({
        'sensor_id': 1,
        'parameter_id': 1,
        'value': 32.1,
    })))

    print(unpack_sensorgram(pack_sensorgram({
        'sensor_id': 1,
        'parameter_id': 1,
        'value': -23,
    })))

    print(unpack_sensorgram(pack_sensorgram({
        'sensor_id': 1,
        'parameter_id': 1,
        'value': [1., 2., 3.],
    })))

    print(unpack_sensorgram(pack_sensorgram({
        'sensor_id': 1,
        'parameter_id': 1,
        'value': (1, [1., 2., 3.]),
    })))
