import unittest
from data import dict_is_subset


class TestData(unittest.TestCase):

    def test_dict_is_subset(self):
        self.assertTrue(dict_is_subset({'type': 'camera/top'},
                                       {'type': 'camera/top', 'res': '800x600'}))
        self.assertFalse(dict_is_subset({'type': 'camera/top', 'foo': 'bar'},
                                        {'type': 'camera/top', 'res': '800x600'}))


if __name__ == '__main__':
    unittest.main()
