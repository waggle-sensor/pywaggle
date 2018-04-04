import unittest
from waggle.protocol.v5.decoder import decode_frame
from waggle.protocol.v5.encoder import encode_frame_from_flat_string


def flatten_sensor_values(sensor_values):
    flattened_values = {}

    for sensor_values in sensor_values.values():
        flattened_values.update(sensor_values)

    return flattened_values


class WaggleProtocolTestUnit(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(decode_frame(encode_frame_from_flat_string('')), {})

    def test_encode(self):
        text = '''
        nc_load_1 0.74
        nc_load_5 0.53
        nc_load_10 0.45
        wagman_ver_git 1ef3
        wagman_time_compile 1522869670
        nc_boot_id 12345678901234567890123456789012
        nc_ram_total 8046136
        nc_ram_free 291328
        net_broadband_rx 123456
        net_broadband_tx 654321
        '''

        encoded_data = encode_frame_from_flat_string(text, verbose=True)
        decoded_data = decode_frame(encoded_data)

        values = flatten_sensor_values(decoded_data)
        print(values)

        self.assertAlmostEqual(values['nc_load_1'], 0.74)
        self.assertAlmostEqual(values['nc_load_5'], 0.53)
        self.assertAlmostEqual(values['nc_load_10'], 0.45)
        self.assertAlmostEqual(values['nc_ram_total'], 8046136)
        self.assertAlmostEqual(values['nc_ram_free'], 291328)
        self.assertAlmostEqual(values['net_broadband_rx'], 123456)
        self.assertAlmostEqual(values['net_broadband_tx'], 654321)

        self.assertEqual(values['wagman_ver_git'], '1ef3')
        self.assertEqual(values['nc_boot_id'], '12345678901234567890123456789012')


if __name__ == '__main__':
    unittest.main()
