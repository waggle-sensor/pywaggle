import unittest
from waggle.data.vision import RGB, BGR
from waggle.data.timestamp import get_timestamp
import numpy as np

class TestData(unittest.TestCase):

    def test_colors(self):
        for fmt in [RGB, BGR]:
            data = np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8)
            data2 = fmt.format_to_cv2(fmt.cv2_to_format(data))
            self.assertTrue(np.all(np.isclose(data, data2, 1.0)), f"checking format {fmt}")
    
    def test_get_timestamp(self):
        ts = get_timestamp()
        self.assertIsInstance(ts, int)

if __name__ == '__main__':
    unittest.main()
