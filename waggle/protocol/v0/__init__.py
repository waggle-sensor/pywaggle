import time
from io import BytesIO
from waggle.checksum import crc8
from binascii import crc_hqx
from binascii import crc32
import unittest

PROTOCOL_MAJOR_VERSION = 2
PROTOCOL_MINOR_VERSION = 1
PROTOCOL_PATCH_VERSION = 0

START_FLAG = 0xaa
END_FLAG = 0x55


def crc16(data, value=0):
    return crc_hqx(data, value)


def get_timestamp_or_now(obj):
    return obj.get('timestamp') or int(time.time())


def validate_user_id(user_id):
    if len(user_id) != 16:
        raise ValueError('Invalid user ID "{}"'.format(user_id.hex()))


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
        response_seq = value.get('response_seq', 0)
        response_sid = value.get('response_sid', 0)

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
        self.encode_int(3, response_seq)
        self.encode_int(2, response_sid)

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

    def decode_waggle_packet(self):
        header = self.decode_bytes(58)
        header_crc = self.decode_int(2)

        if crc16(header) != header_crc:
            raise ValueError('Invalid header CRC.')

        dec = Decoder(BytesIO(header))
        protocol_major_version = dec.decode_int(1)
        protocol_minor_version = dec.decode_int(1)
        protocol_patch_version = dec.decode_int(1)
        message_priority = dec.decode_int(1)
        body_length = dec.decode_int(4)
        timestamp = dec.decode_int(4)
        message_major_version = dec.decode_int(1)
        message_minor_version = dec.decode_int(1)
        reserved = dec.decode_int(2)
        sender_id = dec.decode_bytes(16)
        receiver_id = dec.decode_bytes(16)
        sender_seq = dec.decode_int(3)
        sender_sid = dec.decode_int(2)
        response_seq = dec.decode_int(3)
        response_sid = dec.decode_int(2)

        token = self.decode_int(4)
        body = self.decode_bytes(body_length)
        body_crc = self.decode_int(4)

        if crc32(body) != body_crc:
            raise ValueError('Invalid body CRC.')

        return {
            'timestamp': timestamp,
            'protocol_major_version': protocol_major_version,
            'protocol_minor_version': protocol_minor_version,
            'protocol_patch_version': protocol_patch_version,
            'message_priority': message_priority,
            'message_major_version': message_major_version,
            'message_minor_version': message_minor_version,
            'sender_id': sender_id,
            'sender_seq': sender_seq,
            'sender_sid': sender_sid,
            'receiver_id': receiver_id,
            'response_seq': response_seq,
            'response_sid': response_sid,
            'token': token,
            'body': body,
        }


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

unpack_sensorgrams = make_unpack_function(Decoder.decode_sensorgram)
unpack_datagrams = make_unpack_function(Decoder.decode_datagram)
unpack_waggle_packets = make_unpack_function(Decoder.decode_waggle_packet)


class TestProtocol(unittest.TestCase):

    sensorgram_test_cases = [
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

    def test_encode_decode_sensorgram(self):
        for c in self.sensorgram_test_cases:
            buf = BytesIO()
            enc = Encoder(buf)
            enc.encode_sensorgram(c)
            dec = Decoder(BytesIO(buf.getvalue()))
            r = dec.decode_sensorgram()

            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_pack_unpack_sensorgrams(self):
        results = unpack_sensorgrams(pack_sensorgrams(self.sensorgram_test_cases))

        for c, r in zip(self.sensorgram_test_cases, results):
            for k in c.keys():
                self.assertEqual(c[k], r[k])

    datagram_test_cases = [
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

    def test_encode_decode_datagram(self):
        for c in self.datagram_test_cases:
            buf = BytesIO()
            enc = Encoder(buf)
            enc.encode_datagram(c)
            dec = Decoder(BytesIO(buf.getvalue()))
            r = dec.decode_datagram()

            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_pack_unpack_datagrams(self):
        results = unpack_datagrams(pack_datagrams(self.datagram_test_cases))

        for c, r in zip(self.datagram_test_cases, results):
            for k in c.keys():
                self.assertEqual(c[k], r[k])

    waggle_packet_test_cases = [
        {
            'sender_id': b'0123456789abcdef',
            'receiver_id': b'fedcba9876543210',
            'body': b'^this is a really, really important message!$',
        },
        {
            'timestamp': 123456789,
            'sender_seq': 1,
            'sender_sid': 3,
            'sender_id': b'0123456789abcdef',
            'receiver_id': b'fedcba9876543210',
            'response_seq': 4,
            'response_sid': 9,
            'token': 31243,
            'body': b'^this is a really, really important message!$',
        },
    ]

    def test_encode_decode_waggle_packet(self):
        for c in self.waggle_packet_test_cases:
            buf = BytesIO()
            enc = Encoder(buf)
            enc.encode_waggle_packet(c)
            dec = Decoder(BytesIO(buf.getvalue()))
            r = dec.decode_waggle_packet()

            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_pack_unpack_waggle_packets(self):
        results = unpack_waggle_packets(pack_waggle_packets(self.waggle_packet_test_cases))

        for c, r in zip(self.waggle_packet_test_cases, results):
            for k in c.keys():
                self.assertEqual(c[k], r[k])


if __name__ == '__main__':
    unittest.main()
