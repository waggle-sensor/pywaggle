import unittest
from waggle.data.audio import AudioFolder, AudioSample
from waggle.data.vision import RGB, BGR, ImageFolder, ImageSample
from waggle.data.timestamp import get_timestamp
import numpy as np
from tempfile import TemporaryDirectory
from pathlib import Path
import os.path

class TestData(unittest.TestCase):

    def test_colors(self):
        for fmt in [RGB, BGR]:
            data = np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8)
            data2 = fmt.format_to_cv2(fmt.cv2_to_format(data))
            self.assertTrue(np.all(np.isclose(data, data2, 1.0)), f"checking format {fmt}")
    
    def test_image_save(self):
        with TemporaryDirectory() as dir:
            sample = ImageSample(np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8), 0, RGB)
            for fmt in ["jpg", "png"]:
                name = f"sample.{fmt}"
                sample.save(os.path.join(dir, name))
                sample.save(Path(dir, name))

    def test_image_save_load(self):
        with TemporaryDirectory() as dir:
            sample = ImageSample(np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8), 0, RGB)
            sample.save(Path(dir, "sample.png"))
            samples = ImageFolder(dir, RGB)
            self.assertTrue(np.allclose(sample.data, samples[0].data))
    
    def test_audio_save(self):
        with TemporaryDirectory() as dir:
            # save mono audio
            sample = AudioSample(np.random.uniform(-1, 1, (48000, 1)), 48000, 0)
            name = "sample.wav"
            sample.save(os.path.join(dir, name))
            sample.save(Path(dir, name))

            # save stereo audio
            sample = AudioSample(np.random.uniform(-1, 1, (48000, 2)), 48000, 0)
            name = "sample.wav"
            sample.save(os.path.join(dir, name))
            sample.save(Path(dir, name))

    def test_audio_save_load(self):
        with TemporaryDirectory() as dir:
            sample = AudioSample(np.random.uniform(-1, 1, (48000, 1)), 48000, 0)
            sample.save(Path(dir, "sample.wav"))
            samples = AudioFolder(dir)
            self.assertTrue(np.allclose(sample.data, samples[0].data, atol=1e-4))

            sample = AudioSample(np.random.uniform(-1, 1, (48000, 2)), 48000, 0)
            sample.save(Path(dir, "sample.wav"))
            samples = AudioFolder(dir)
            self.assertTrue(np.allclose(sample.data, samples[0].data, atol=1e-4))


    def test_get_timestamp(self):
        ts = get_timestamp()
        self.assertIsInstance(ts, int)

if __name__ == '__main__':
    unittest.main()
