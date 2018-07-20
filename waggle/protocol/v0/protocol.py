import time
from io import BytesIO
from waggle.checksum import crc8
from binascii import crc_hqx
from binascii import crc32
import random


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
        length = self.writer.write(value)

        if length != len(value):
            raise IOError('Failed to encode bytes.')

    def encode_int(self, length, value):
        self.encode_bytes(value.to_bytes(length, 'big'))

    def encode_sensorgram(self, value):
        sensor_id = value['sensor_id']
        sensor_instance = value.get('sensor_instance', 0)
        parameter_id = value['parameter_id']
        timestamp = get_timestamp_or_now(value)
        body = value['value']
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
        message_major_type = value.get('message_major_type', 0)
        message_minor_type = value.get('message_minor_type', 0)
        reserved = 0

        sender_id = bytes.fromhex(value.get('sender_id', '0000000000000000'))
        assert_length(sender_id, 8)

        sender_sub_id = bytes.fromhex(value.get('sender_sub_id', '0000000000000000'))
        assert_length(sender_sub_id, 8)

        receiver_id = bytes.fromhex(value.get('receiver_id', '0000000000000000'))
        assert_length(receiver_id, 8)

        receiver_sub_id = bytes.fromhex(value.get('receiver_sub_id', '0000000000000000'))
        assert_length(receiver_sub_id, 8)

        sender_seq = value.get('sender_seq', get_sender_sequence_number())
        sender_sid = value.get('sender_sid', 0)
        response_seq = value.get('response_seq', 0)
        response_sid = value.get('response_sid', 0)

        self.encode_int(1, protocol_major_version)
        self.encode_int(1, protocol_minor_version)
        self.encode_int(1, protocol_patch_version)
        self.encode_int(1, message_priority)
        self.encode_int(4, body_length)
        self.encode_int(4, timestamp)
        self.encode_int(1, message_major_type)
        self.encode_int(1, message_minor_type)
        self.encode_int(2, reserved)
        self.encode_bytes(sender_id)
        self.encode_bytes(sender_sub_id)
        self.encode_bytes(receiver_id)
        self.encode_bytes(receiver_sub_id)
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
            'value': body,
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
        message_major_type = dec.decode_int(1)
        message_minor_type = dec.decode_int(1)
        reserved = dec.decode_int(2)
        sender_id = dec.decode_bytes(8).hex()
        sender_sub_id = dec.decode_bytes(8).hex()
        receiver_id = dec.decode_bytes(8).hex()
        receiver_sub_id = dec.decode_bytes(8).hex()
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
