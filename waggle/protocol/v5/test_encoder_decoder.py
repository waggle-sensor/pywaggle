# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
from waggle.protocol.v5.decoder import decode_frame
from waggle.protocol.v5.encoder import encode_frame


class WaggleProtocolTestUnit(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(decode_frame(encode_frame({})), {})

    def test_encode(self):
        data = {
            0x50: ['010203040506'],
            0x71: ['73c02022aeab4e7fb5ac6be2b0d7d771'],
            0x5A: [123, 234, 345, 456, 567, 678],
            0x07: [123, 234, 345],
        }

        encoded_data = encode_frame(data)
        self.assertIsInstance(encoded_data, bytes)

        decoded_data = decode_frame(encoded_data)

        for sensor_id in data.keys():
            self.assertIn(sensor_id, decoded_data)
            decoded_values = decoded_data[sensor_id]
            self.assertIsInstance(decoded_values, dict)
            decoded_values = list(decoded_values.values())
            original_values = data[sensor_id]
            self.assertEqual(decoded_values, original_values)


if __name__ == '__main__':
    unittest.main()
