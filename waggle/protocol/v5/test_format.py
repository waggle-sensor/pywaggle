# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
import format


class WaggleFormatTest(unittest.TestCase):

    def test_uint8(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**8-1,
        ]

        for example in examples:
            formats = ['uint']
            lengths = [1]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_uint16(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**8-1,
            2**16-1,
        ]

        for example in examples:
            formats = ['uint']
            lengths = [2]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_uint24(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**8-1,
            2**16-1,
            2**24-1,
        ]

        for example in examples:
            formats = ['uint']
            lengths = [3]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_uint32(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**8-1,
            2**16-1,
            2**24-1,
            2**32-1,
        ]

        for example in examples:
            formats = ['uint']
            lengths = [4]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_int8(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**7-1,
        ]

        for example in examples:
            formats = ['int']
            lengths = [1]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

            formats = ['int']
            lengths = [1]
            values = [-example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_int16(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**7-1,
            2**15-1,
        ]

        for example in examples:
            formats = ['int']
            lengths = [2]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

            formats = ['int']
            lengths = [2]
            values = [-example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_int24(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**7-1,
            2**15-1,
            2**23-1,
        ]

        for example in examples:
            formats = ['int']
            lengths = [3]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

            formats = ['int']
            lengths = [3]
            values = [-example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_int32(self):
        examples = [
            0,
            1,
            2,
            3,
            5,
            7,
            11,
            2**7-1,
            2**15-1,
            2**23-1,
            2**31-1,
        ]

        for example in examples:
            formats = ['int']
            lengths = [4]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

            formats = ['int']
            lengths = [4]
            values = [-example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_float32(self):
        examples = [
            0.0,
            1.0,
            -1.0,
            -1234.56789,
            1234.56789,
        ]

        for example in examples:
            formats = ['float']
            lengths = [4]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertEqual(len(values), len(unpacked))
            self.assertAlmostEqual(values[0], unpacked[0], places=4)

    def test_float64(self):
        examples = [
            0.0,
            1.0,
            -1.0,
            -1234.56789,
            1234.56789,
        ]

        for example in examples:
            formats = ['float']
            lengths = [8]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertEqual(len(values), len(unpacked))
            self.assertAlmostEqual(values[0], unpacked[0], places=8)

    def test_string(self):
        examples = [
            '',
            'hello',
            'testing',
            'x' * 100,
        ]

        for example in examples:
            formats = ['str']
            lengths = [len(example)]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)

    def test_hex(self):
        examples = [
            '',
            '12',
            'aa55aa55',
            '123456',
        ]

        for example in examples:
            formats = ['hex']
            lengths = [len(example) // 2]
            values = [example]

            packed = format.waggle_pack(formats, lengths, values)
            unpacked = format.waggle_unpack(formats, lengths, packed)
            self.assertListEqual(values, unpacked)


if __name__ == '__main__':
    unittest.main()
