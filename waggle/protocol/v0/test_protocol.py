import unittest
from protocol import *


class TestProtocol(unittest.TestCase):

    sensorgram_test_cases = [
        {
            'sensor_id': 1,
            'parameter_id': 2,
            'value': b'',
        },
        {
            'sensor_id': 1,
            'parameter_id': 2,
            'value': b'123',
        },
        {
            'timestamp': 1234567,
            'sensor_id': 2,
            'sensor_instance': 7,
            'parameter_id': 4,
            'value': b'abc',
        },
        {
            'sensor_id': 1,
            'parameter_id': 2,
            'value': b'x' * 4096,
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
        {
            'plugin_id': 1,
            'body': b'x' * 4096,
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
            'sender_id': '0000000000000001',
            'sender_sub_id': '0000000000000003',
            'receiver_id': '0000000000000002',
            'receiver_sub_id': '0000000000000004',
            'body': b'^this is a really, really important message!$',
        },
        {
            'timestamp': 123456789,
            'sender_seq': 1,
            'sender_sid': 3,
            'sender_id': '0000000000000001',
            'sender_sub_id': '0000000000000003',
            'receiver_id': '0000000000000002',
            'receiver_sub_id': '0000000000000004',
            'response_seq': 4,
            'response_sid': 9,
            'token': 31243,
            'body': b'^this is a really, really important message!$',
        },
        {
            'timestamp': 100100100,
            'sender_id': '0000000000000001',
            'sender_sub_id': '0000000000000003',
            'receiver_id': '0000000000000002',
            'receiver_sub_id': '0000000000000004',
            'body': b'x' * 4096,
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
