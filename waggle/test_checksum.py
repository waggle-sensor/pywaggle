import unittest
import checksum


class ChecksumTestCase(unittest.TestCase):

    def test_crc8(self):
        test_cases = [
            (bytes([]), 0),
            (bytes([0x80]), 0x8c),
            (bytes([1, 2, 3]), 216),
            (bytes([0xff] * 1024), 201),
        ]

        for data, crc in test_cases:
            self.assertEqual(checksum.crc8(data), crc)


if __name__ == '__main__':
    unittest.main()
