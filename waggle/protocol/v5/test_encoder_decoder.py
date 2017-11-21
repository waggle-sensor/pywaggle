import unittest

from waggle.protocol.v5 import decoder
from waggle.protocol.v5 import encoder

class WaggleProtocolTestUnit(unittest.TestCase):

    def test_encode(self):
        data = {
            0x50: ['010203040506'],
            0x1D: [100, 30],
            0x5A: [123, 234, 345, 456, 567, 678],
            0x07: [123, 234, 345],
        }    
        encoded_data = encoder.encode_frame(data)
        decoded_data = decoder.decode_frame(encoded_data)
        for sensor in data:
            # self.assertIn(decoded_data, sensor)
            decoded_values = decoded_data.get(sensor)
            print(decoded_values)
            self.assertNotEqual(decoded_values, None)
            self.assertIsInstance(decoded_values, dict)
            decoded_values = list(decoded_values.values())
            original_values = data[sensor]
            print('%s encoded/decoded to %s' % (str(original_values), str(decoded_values)))
            self.assertEqual(len(decoded_values), len(original_values))

            
        # self.assertEqual()


if __name__ == '__main__':
    unittest.main()
