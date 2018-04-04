import unittest
from waggle.protocol.v5.decoder import decode_frame
from waggle.protocol.v5.encoder import encode_frame


class WaggleProtocolTestUnit(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(decode_frame(encode_frame({})), {})

    def test_encode(self):
        data = {
            0x50: ['010203040506'],
            # 0x71: ['73c02022aeab4e7fb5ac6be2b0d7d771'],
            # 0x1D: [100, 30],
            0x5A: [123, 234, 345, 456, 567, 678],
            0x07: [123, 234, 345],
            0x7C: [False, True, False, True],
            0x78: ['%15s' % ('abcde',)]
        }

        encoded_data = encode_frame(data)
        decoded_data = decode_frame(encoded_data)

        for sensor in data:
            # self.assertIn(decoded_data, sensor)
            decoded_values = decoded_data.get(sensor)

            self.assertNotEqual(decoded_values, None)
            self.assertIsInstance(decoded_values, dict)
            decoded_values = list(decoded_values.values())
            original_values = data[sensor]
            self.assertEqual(len(decoded_values), len(original_values))


if __name__ == '__main__':
    unittest.main()
