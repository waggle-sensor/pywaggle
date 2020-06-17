# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
from waggle.checksum import crc8


class ChecksumTestCase(unittest.TestCase):

    def test_crc8(self):
        test_cases = [
            (bytes([]), 0),
            (bytes([0x80]), 0x8c),
            (bytes([1, 2, 3]), 216),
            (bytes([0xff] * 1024), 201),
        ]

        for data, crc in test_cases:
            self.assertEqual(crc8(data), crc)


if __name__ == '__main__':
    unittest.main()
