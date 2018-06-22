import time
from io import BytesIO
from waggle.checksum import crc8
from binascii import crc_hqx as crc16
from binascii import crc32
import unittest

PROTOCOL_MAJOR_VERSION = 2
PROTOCOL_MINOR_VERSION = 1
PROTOCOL_PATCH_VERSION = 0

START_FLAG = 0xaa
END_FLAG = 0x55


class Encoder:

    def __init__(self, writer):
        self.writer = writer

    def encode_int(self, length, value):
        self.writer.write(value.to_bytes(length, 'big'))

    def encode_bytes(self, value):
        self.writer.write(value)

    def encode_sensorgram(self, value):
        sensor_id = value['sensor_id']
        sensor_instance = value.get('sensor_instance', 0)
        parameter_id = value['parameter_id']
        timestamp = get_timestamp_or_now(value)
        body = value['body']
        body_length = len(body)

        self.encode_int(2, body_length)
        self.encode_int(2, sensor_id)
        self.encode_int(1, sensor_instance)
        self.encode_int(1, parameter_id)
        self.encode_int(4, timestamp)
        self.encode_bytes(body)

    def encode_datagram(self, value):
        protocol_version = value.get('protocol_version', PROTOCOL_MAJOR_VERSION)
        timestamp = get_timestamp_or_now(value)
        packet_seq = 0
        packet_type = 0
        plugin_id = value['plugin_id']
        plugin_major_version = value.get('plugin_major_version', 0)
        plugin_minor_version = value.get('plugin_minor_version', 0)
        plugin_patch_version = value.get('plugin_patch_version', 0)
        plugin_instance = value.get('plugin_instance', 0)
        plugin_run_id = value.get('plugin_run_id', 0)
        body = value['body']
        body_length = len(body)
        body_crc = crc8(body)

        self.encode_int(1, START_FLAG)
        self.encode_int(3, body_length)
        self.encode_int(1, protocol_version)
        self.encode_int(4, timestamp)
        self.encode_int(2, packet_seq)
        self.encode_int(1, packet_type)
        self.encode_int(2, plugin_id)
        self.encode_int(1, plugin_major_version)
        self.encode_int(1, plugin_minor_version)
        self.encode_int(1, plugin_patch_version)
        self.encode_int(1, plugin_instance)
        self.encode_int(2, plugin_run_id)
        self.encode_bytes(body)
        self.encode_int(1, body_crc)
        self.encode_int(1, END_FLAG)

    def encode_waggle_packet_header(self, value):
        protocol_major_version = value.get('protocol_major_version', PROTOCOL_MAJOR_VERSION)
        protocol_minor_version = value.get('protocol_major_version', PROTOCOL_MINOR_VERSION)
        protocol_patch_version = value.get('protocol_major_version', PROTOCOL_PATCH_VERSION)
        message_priority = value.get('message_priority', 0)
        body = value['body']
        body_length = len(body)
        timestamp = get_timestamp_or_now(value)
        message_major_version = value.get('message_major_version', 0)
        message_minor_version = value.get('message_minor_version', 0)
        reserved = 0

        sender_id = value['sender_id']
        validate_user_id(sender_id)

        receiver_id = value['receiver_id']
        validate_user_id(receiver_id)

        sender_seq = value.get('sender_seq', 0)
        sender_sid = value.get('sender_sid', 0)
        receiver_seq = value.get('receiver_seq', 0)
        receiver_sid = value.get('receiver_sid', 0)

        self.encode_int(1, protocol_major_version)
        self.encode_int(1, protocol_minor_version)
        self.encode_int(1, protocol_patch_version)
        self.encode_int(1, message_priority)
        self.encode_int(4, body_length)
        self.encode_int(4, timestamp)
        self.encode_int(1, message_major_version)
        self.encode_int(1, message_minor_version)
        self.encode_int(2, reserved)
        self.encode_bytes(sender_id)
        self.encode_bytes(receiver_id)
        self.encode_int(3, sender_seq)
        self.encode_int(2, sender_sid)
        self.encode_int(3, receiver_seq)
        self.encode_int(2, receiver_sid)

    def encode_waggle_packet(self, value):
        b = BytesIO()
        enc = Encoder(b)
        enc.encode_waggle_packet_header(value)

        header = b.getvalue()
        header_crc = crc16(header, 0)
        token = value.get('token')
        body = value['body']
        body_crc = crc32(value['body'])

        self.encode_bytes(header)
        self.encode_int(2, header_crc)
        self.encode_int(4, token)
        self.encode_bytes(body)
        self.encode_int(4, body_crc)


class Decoder:

    def __init__(self, reader):
        self.reader = reader

    def decode_bytes(self, length):
        b = self.reader.read(length)

        if len(b) != length:
            raise EOFError()

        return b

    def decode_int(self, length):
        return int.from_bytes(self.decode_bytes(length), 'big')

    def decode_sensorgram(self):
        body_length = self.decode_int(2)
        sensor_id = self.decode_int(2)
        sensor_instance = self.decode_int(1)
        parameter_id = self.decode_int(1)
        timestamp = self.decode_int(4)
        body = self.decode_bytes(body_length)

        return {
            'sensor_id': sensor_id,
            'sensor_instance': sensor_instance,
            'parameter_id': parameter_id,
            'timestamp': timestamp,
            'body': body,
        }

    def decode_datagram(self):
        start_flag = self.decode_int(1)

        if start_flag != START_FLAG:
            raise ValueError('Invalid start flag.')

        body_length = self.decode_int(3)
        protocol_version = self.decode_int(1)
        timestamp = self.decode_int(4)
        packet_seq = self.decode_int(2)
        packet_type = self.decode_int(1)
        plugin_id = self.decode_int(2)
        plugin_major_version = self.decode_int(1)
        plugin_minor_version = self.decode_int(1)
        plugin_patch_version = self.decode_int(1)
        plugin_instance = self.decode_int(1)
        plugin_run_id = self.decode_int(2)
        body = self.decode_bytes(body_length)
        body_crc = self.decode_int(1)

        if crc8(body) != body_crc:
            raise ValueError('Invalid body CRC.')

        end_flag = self.decode_int(1)

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


def get_timestamp_or_now(obj):
    return obj.get('timestamp') or int(time.time())


def validate_user_id(user_id):
    if len(user_id) != 16:
        raise ValueError('Invalid user ID "{}"'.format(user_id.hex()))


def write_waggle_packet(w, packet):
    encoder = Encoder(w)
    encoder.encode_waggle_packet(packet)


def read_waggle_packet(r):
    # check protocol version
    assert read_uint(r, 1) == PROTOCOL_MAJOR_VERSION
    read_uint(r, 1) # ignore minor version
    read_uint(r, 1) # ignore major version

    write_uint(w, 1, packet.get('priority', 0))
    write_uint(w, 4, len(packet['body']))
    write_uint(w, 4, get_timestamp_or_now(packet))
    write_uint(w, 1, packet.get('message_major_version', 0))
    write_uint(w, 1, packet.get('message_minor_version', 0))
    write_uint(w, 2, 0) # reserved
    w.write(packet['sender_id'])
    w.write(packet['receiver_id'])
    write_uint(w, 3, packet.get('sender_seq', 0))
    write_uint(w, 2, packet.get('sender_sid', 0))
    write_uint(w, 3, packet.get('receiver_seq', 0))
    write_uint(w, 2, packet.get('receiver_sid', 0))
    write_uint(w, 2, 0) # fix crc
    write_uint(w, 4, packet.get('token', 0))
    w.write(packet['body'])
    write_uint(w, 4, crc32(packet['body']))


def pack_sensorgrams(sensorgrams):
    b = BytesIO()
    encoder = Encoder(b)


    for sensorgram in sensorgrams:
        encoder.encode_sensorgram(sensorgram)

    return b.getvalue()


def unpack_sensorgrams(b):
    sensorgrams = []

    decoder = Decoder(BytesIO(b))

    while True:
        try:
            sensorgrams.append(decoder.decode_sensorgram())
        except EOFError:
            break

    return sensorgrams


def pack_datagram(datagram):
    b = BytesIO()
    encoder = Encoder(b)
    encoder.encode_datagram(datagram)
    return b.getvalue()


def unpack_datagram(b):
    decoder = Decoder(BytesIO(b))
    return decoder.decode_datagram()


class TestProtocol(unittest.TestCase):

    def test_sensorgram_pack_unpack(self):
        cases = [
            {
                'sensor_id': 1,
                'parameter_id': 1,
                'body': b'',
            },
            {
                'sensor_id': 1,
                'parameter_id': 2,
                'body': b'123',
            },
            {
                'sensor_id': 2,
                'parameter_id': 4,
                'body': b'aaaaaaaaax',
            },
            {
                'sensor_id': 2,
                'sensor_instance': 7,
                'parameter_id': 4,
                'body': b'abc',
            },
            {
                'timestamp': 1234567,
                'sensor_id': 2,
                'parameter_id': 4,
                'body': b'ABC',
            },
        ]

        for c in cases:
            r = unpack_sensorgrams(pack_sensorgrams([c]))[0]

            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_datagram_pack_unpack(self):
        cases = [
            {
                'plugin_id': 1,
                'body': b'',
            },
            {
                'plugin_id': 1,
                'body': b'123',
            },
            {
                'timestamp': 1234567,
                'plugin_id': 9090,
                'plugin_major_version': 1,
                'plugin_minor_version': 3,
                'plugin_patch_version': 7,
                'plugin_instance': 9,
                'plugin_run_id': 12345,
                'body': b'123',
            },
        ]

        for c in cases:
            r = unpack_datagram(pack_datagram(c))

            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_waggle_packet_pack_unpack(self):
        cases = [
            {
                'sender_id': b'0123456789abcdef',
                'receiver_id': b'fedcba9876543210',
                'body': b'^this is a really, really important message!$',
            },
        ]


        for c in cases:
            w = BytesIO()
            write_waggle_packet(w, c)
            print(w.getvalue())
            # r = unpack_datagram(pack_datagram(c))
            #
            # for k in c.keys():
            #     self.assertEqual(c[k], r[k])


if __name__ == '__main__':
    unittest.main()
