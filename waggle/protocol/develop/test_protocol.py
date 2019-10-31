# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
from protocol import encode_values, decode_values
from protocol import pack_sensorgram, unpack_sensorgram
from protocol import pack_datagram, unpack_datagram
from protocol import pack_message, unpack_message

value_test_cases = [
    b'hello',
    'hello as a string',
    0,
    0x12,
    0xff,
    0x1234,
    0xffff,
    0x123456,
    0xffffff,
    0x12345678,
    0xffffffff,
    b'x' * 10000,
]

sensorgram_test_cases = [
    {'id': 1, 'sub_id': 2, 'value': b''},
    {'id': 1, 'sub_id': 2, 'value': b'123'},
    {'timestamp': 1234567, 'id': 2, 'inst': 7, 'sub_id': 4, 'value': b'abc'},
    {'id': 1, 'sub_id': 2, 'value': b'x' * 4096},
]

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

message_test_cases = [
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


class TestProtocol(unittest.TestCase):

    def test_values(self):
        for c in value_test_cases:
            self.assertAlmostEqual(c, decode_values(encode_values(c)))

    def test_sensorgrams(self):
        for c in sensorgram_test_cases:
            r = unpack_sensorgram(pack_sensorgram(c))
            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_datagrams(self):
        for c in datagram_test_cases:
            r = unpack_datagram(pack_datagram(c))
            for k in c.keys():
                self.assertEqual(c[k], r[k])

    def test_messages(self):
        for c in message_test_cases:
            r = unpack_message(pack_message(c))
            for k in c.keys():
                self.assertEqual(c[k], r[k])


if __name__ == '__main__':
    unittest.main()