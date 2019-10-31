# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
from io import BytesIO
from protocol import encode_values, decode_values
from protocol import pack_sensorgram, unpack_sensorgram

value_test_cases = [
    b'hello',
    'hello as a string',
    0,
    100,
    200,
]

sensorgram_test_cases = [
    {'id': 1, 'sub_id': 2, 'value': b''},
    {'id': 1, 'sub_id': 2, 'value': b'123'},
    {'timestamp': 1234567, 'id': 2, 'inst': 7, 'sub_id': 4, 'value': b'abc'},
    {'id': 1, 'sub_id': 2, 'value': b'x' * 4096},
]


class TestProtocol(unittest.TestCase):

    def test_values(self):
        for c in value_test_cases:
            self.assertAlmostEqual(c, decode_values(encode_values(c)))

    def test_pack_unpack_sensorgrams(self):
        for c in sensorgram_test_cases:
            r = unpack_sensorgram(pack_sensorgram(c))
            for k in c.keys():
                self.assertEqual(c[k], r[k])

    # datagram_test_cases = [
    #     {
    #         'plugin_id': 1,
    #         'body': b'',
    #     },
    #     {
    #         'plugin_id': 1,
    #         'body': b'123',
    #     },
    #     {
    #         'timestamp': 1234567,
    #         'plugin_id': 9090,
    #         'plugin_major_version': 1,
    #         'plugin_minor_version': 3,
    #         'plugin_patch_version': 7,
    #         'plugin_instance': 9,
    #         'plugin_run_id': 12345,
    #         'body': b'123',
    #     },
    #     {
    #         'plugin_id': 1,
    #         'body': b'x' * 4096,
    #     },
    # ]

    # def test_encode_decode_datagram(self):
    #     for c in self.datagram_test_cases:
    #         buf = BytesIO()
    #         enc = Encoder(buf)
    #         enc.encode_datagram(c)
    #         dec = Decoder(BytesIO(buf.getvalue()))
    #         r = dec.decode_datagram()

    #         for k in c.keys():
    #             self.assertEqual(c[k], r[k])

    # def test_pack_unpack_datagrams(self):
    #     results = unpack_datagrams(pack_datagrams(self.datagram_test_cases))

    #     for c, r in zip(self.datagram_test_cases, results):
    #         for k in c.keys():
    #             self.assertEqual(c[k], r[k])

    # waggle_packet_test_cases = [
    #     {
    #         'sender_id': '0000000000000001',
    #         'sender_sub_id': '0000000000000003',
    #         'receiver_id': '0000000000000002',
    #         'receiver_sub_id': '0000000000000004',
    #         'body': b'^this is a really, really important message!$',
    #     },
    #     {
    #         'timestamp': 123456789,
    #         'sender_seq': 1,
    #         'sender_sid': 3,
    #         'sender_id': '0000000000000001',
    #         'sender_sub_id': '0000000000000003',
    #         'receiver_id': '0000000000000002',
    #         'receiver_sub_id': '0000000000000004',
    #         'response_seq': 4,
    #         'response_sid': 9,
    #         'token': 31243,
    #         'body': b'^this is a really, really important message!$',
    #     },
    #     {
    #         'timestamp': 100100100,
    #         'sender_id': '0000000000000001',
    #         'sender_sub_id': '0000000000000003',
    #         'receiver_id': '0000000000000002',
    #         'receiver_sub_id': '0000000000000004',
    #         'body': b'x' * 4096,
    #     },
    # ]

    # def test_encode_decode_waggle_packet(self):
    #     for c in self.waggle_packet_test_cases:
    #         buf = BytesIO()
    #         enc = Encoder(buf)
    #         enc.encode_waggle_packet(c)
    #         dec = Decoder(BytesIO(buf.getvalue()))
    #         r = dec.decode_waggle_packet()

    #         for k in c.keys():
    #             self.assertEqual(c[k], r[k])

    # def test_pack_unpack_waggle_packets(self):
    #     results = unpack_waggle_packets(
    #         pack_waggle_packets(self.waggle_packet_test_cases))

    #     for c, r in zip(self.waggle_packet_test_cases, results):
    #         for k in c.keys():
    #             self.assertEqual(c[k], r[k])

    # def test_typed(self):
    #     testcases = [
    #         {'id': 1, 'sub_id': 1, 'value': b'bytes'},
    #         {'id': 1, 'sub_id': 1, 'value': 'string'},
    #         {'id': 1, 'sub_id': 1, 'value': True},
    #         {'id': 1, 'sub_id': 1, 'value': False},
    #         {'id': 1, 'sub_id': 1, 'value': None},
    #         {'id': 1, 'sub_id': 1, 'value': 1},
    #         {'id': 1, 'sub_id': 1, 'value': 12},
    #         {'id': 1, 'sub_id': 1, 'value': 123},
    #         {'id': 1, 'sub_id': 1, 'value': 1234},
    #         {'id': 1, 'sub_id': 1, 'value': 123456},
    #         {'id': 1, 'sub_id': 1, 'value': 123456789},
    #         {'id': 1, 'sub_id': 1, 'value': 1234567890000},
    #         {'id': 1, 'sub_id': 1, 'value': -1},
    #         {'id': 1, 'sub_id': 1, 'value': -12},
    #         {'id': 1, 'sub_id': 1, 'value': -123},
    #         {'id': 1, 'sub_id': 1, 'value': -1234},
    #         {'id': 1, 'sub_id': 1, 'value': -123456},
    #         {'id': 1, 'sub_id': 1, 'value': -123456789},
    #         {'id': 1, 'sub_id': 1, 'value': -1234567890000},
    #         {'id': 1, 'sub_id': 1, 'value': 13.2},
    #         {'id': 1, 'sub_id': 1, 'value': [1.2, 3.2, 4.5, 9.3]},
    #     ]

    #     for t in testcases:
    #         v1 = t['value']
    #         v2 = decode_value_type(encode_value_type(t))['value']

    #         if isinstance(v1, list):
    #             self.assertEqual(len(v1), len(v2))

    #             for x, y in zip(v1, v2):
    #                 self.assertAlmostEqual(x, y, 5)
    #         elif isinstance(v1, float):
    #             self.assertAlmostEqual(v1, v2, 5)
    #         else:
    #             self.assertEqual(v1, v2)


if __name__ == '__main__':
    unittest.main()
