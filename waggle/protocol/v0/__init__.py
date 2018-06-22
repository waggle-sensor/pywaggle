import time
from io import BytesIO
from waggle.checksum import crc8
from binascii import crc_hqx as crc16
from binascii import crc32
import unittest


def get_timestamp_or_now(obj):
    if 'timestamp' in obj:
        return obj['timestamp']
    return int(time.time())


def write_uint(w, n, x):
    w.write(x.to_bytes(n, 'big', signed=False))


def read_uint(r, n):
    return int.from_bytes(r.read(n), 'big', signed=False)


def write_sensorgram(w, sensorgram):
    write_uint(w, 2, len(sensorgram['body']))
    write_uint(w, 2, sensorgram['sensor_id'])
    write_uint(w, 1, sensorgram.get('sensor_instance', 0))
    write_uint(w, 1, sensorgram['parameter_id'])
    write_uint(w, 4, get_timestamp_or_now(sensorgram))
    w.write(sensorgram['body'])


def read_sensorgram(r):
    body_length = read_uint(r, 2)

    sensorgram = {
        'sensor_id': read_uint(r, 2),
        'sensor_instance': read_uint(r, 1),
        'parameter_id': read_uint(r, 1),
        'timestamp': read_uint(r, 4),
        'body': r.read(body_length),
    }

    assert body_length == len(sensorgram['body'])

    return sensorgram


def write_datagram(w, datagram):
    write_uint(w, 1, 0xaa)
    write_uint(w, 3, len(datagram['body']))
    write_uint(w, 1, datagram.get('protocol_version', 2))
    write_uint(w, 4, get_timestamp_or_now(datagram))
    write_uint(w, 2, datagram.get('packet_seq', 0))
    write_uint(w, 1, datagram.get('packet_type', 0))
    write_uint(w, 2, datagram['plugin_id'])
    write_uint(w, 1, datagram.get('plugin_major_version', 0))
    write_uint(w, 1, datagram.get('plugin_minor_version', 0))
    write_uint(w, 1, datagram.get('plugin_patch_version', 0))
    write_uint(w, 1, datagram.get('plugin_instance', 0))
    write_uint(w, 2, datagram.get('plugin_run_id', 0))
    w.write(datagram['body'])
    write_uint(w, 1, crc8(datagram['body']))
    write_uint(w, 1, 0x55)


def read_datagram(r):
    assert read_uint(r, 1) == 0xaa
    body_length = read_uint(r, 3)

    datagram = {
        'protocol_version': read_uint(r, 1),
        'timestamp': read_uint(r, 4),
        'packet_seq': read_uint(r, 2),
        'packet_type': read_uint(r, 1),
        'plugin_id': read_uint(r, 2),
        'plugin_major_version': read_uint(r, 1),
        'plugin_minor_version': read_uint(r, 1),
        'plugin_patch_version': read_uint(r, 1),
        'plugin_instance': read_uint(r, 1),
        'plugin_run_id': read_uint(r, 2),
        'body': r.read(body_length),
    }

    assert body_length == len(datagram['body'])
    assert read_uint(r, 1) == crc8(datagram['body'])
    assert read_uint(r, 1) == 0x55

    return datagram


def write_waggle_packet(w, packet):
    assert len(packet['sender_id']) == 16
    assert len(packet['receiver_id']) == 16

    write_uint(w, 1, packet.get('protocol_major_version', 2))
    write_uint(w, 1, packet.get('protocol_minor_version', 0))
    write_uint(w, 1, packet.get('protocol_patch_version', 0))
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


def pack_sensorgram(sensorgram):
    w = BytesIO()
    write_sensorgram(w, sensorgram)
    return w.getvalue()


def unpack_sensorgram(b):
    return read_sensorgram(BytesIO(b))


def pack_sensorgrams(*sensorgrams):
    w = BytesIO()

    for sensorgram in sensorgrams:
        write_sensorgram(w, sensorgram)

    return w.getvalue()


def unpack_sensorgram(b):
    return read_sensorgram(BytesIO(b))


def pack_datagram(datagram):
    w = BytesIO()
    write_datagram(w, datagram)
    return w.getvalue()


def unpack_datagram(b):
    return read_datagram(BytesIO(b))


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
            r = unpack_sensorgram(pack_sensorgram(c))

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


if __name__ == '__main__':
    print(pack_sensorgrams(
        {
            'sensor_id': 1,
            'body': b'123',
        },
        {
            'sensor_id': 1,
            'body': b'123',
        },
        {
            'sensor_id': 1,
            'body': b'123',
        },
        {
            'sensor_id': 1,
            'body': b'123',
        },
    ))

    unittest.main()
