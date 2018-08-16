import unittest
import checksum


class ChecksumTestCase(unittest.TestCase):

    def test_polynomial_is_8c(self):
        self.assertEqual(checksum.crc8(bytes([0x80])), 0x8c)


if __name__ == '__main__':
    unittest.main()
