import unittest

import decode
import encode

class WaggleProtocolTestUnit(unittest.TestCase):

    def test_encode(self):
        data = {0x50: [b'\x01\x02\x03\x04\x05\x06']}
