# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
from waggle.coresense.utils import decode_frame


class TestUtils(unittest.TestCase):

    def test_decode_empty(self):
        frame = bytes([0xAA, 0, 0, 0, 0x55])
        data = decode_frame(frame)
        self.assertEqual(data, {})

    def test_decode_invalid_start(self):
        frame = bytes([0xAB, 0, 0, 0, 0x55])
        with self.assertRaisesRegex(RuntimeError, 'invalid start'):
            decode_frame(frame)

    def test_decode_invalid_end(self):
        frame = bytes([0xAA, 0, 0, 0, 0x15])
        with self.assertRaisesRegex(RuntimeError, 'invalid end'):
            decode_frame(frame)

    def test_decode_invalid_length(self):
        frame = bytes([0xAA, 0, 3, 0, 0x55])
        with self.assertRaisesRegex(RuntimeError, 'invalid length'):
            decode_frame(frame)

    def test_decode_invalid_crc(self):
        frame = bytes([0xAA, 0, 1, 7, 2, 0x55])
        with self.assertRaisesRegex(RuntimeError, 'invalid crc'):
            decode_frame(frame)


if __name__ == '__main__':
    unittest.main()
