import unittest

import format
from bitstring import BitArray

class WaggleFormatTest(unittest.TestCase):

    # Test unsinged int up to 2^32
    def test_unsigned_int(self):
        for x in range(0, 32):
            value = pow(2, x)
            length = float(x + 1) / 8
            packed_bit = format.pack_unsigned_int(value, length)
            packed_byte = BitArray(bin=packed_bit).tobytes()
            unpacked = format.unpack_unsigned_int(packed_byte, 0, length)
            
            self.assertEqual(value, unpacked)

    def test_signed_int(self):
        # For negetives
        for x in range(0, 32):
            value = -pow(2, x)
            length = float(x + 1) / 8
            packed_bit = format.pack_signed_int(value, length)
            packed_byte = BitArray(bin=packed_bit).tobytes()
            unpacked = format.unpack_signed_int(packed_byte, 0, length)
            
            self.assertEqual(value, unpacked)
        
        # For positives
        for x in range(0, 32):
            value = pow(2, x) - 1
            length = float(x + 1) / 8
            packed_bit = format.pack_signed_int(value, length)
            packed_byte = BitArray(bin=packed_bit).tobytes()
            unpacked = format.unpack_signed_int(packed_byte, 0, length)
            
            self.assertEqual(value, unpacked)

    def test_float(self):
        for value in [-1234.56789, 1234.56789]:
            pass
            

if __name__ == '__main__':
    unittest.main()