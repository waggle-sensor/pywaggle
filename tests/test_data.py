import unittest
from waggle.data.audio import AudioFolder, AudioSample
from waggle.data.vision import RGB, BGR, ImageFolder, ImageSample, resolve_device
from waggle.data.timestamp import get_timestamp
import numpy as np
from tempfile import TemporaryDirectory
from pathlib import Path
import os.path
from itertools import product


def generate_audio_data(samplerate, channels, dtype):
    if dtype == np.float32:
        return np.random.uniform(-1, 1, (samplerate, channels)).astype(dtype)
    if dtype == np.float64:
        return np.random.uniform(-1, 1, (samplerate, channels)).astype(dtype)
    if dtype == np.int16:
        return np.random.randint(
            -(2**15), 2**15, (samplerate, channels), dtype=dtype
        )
    if dtype == np.int32:
        return np.random.randint(
            -(2**31), 2**31, (samplerate, channels), dtype=dtype
        )
    raise ValueError("unsupported audio settings")


def generate_audio_sample(samplerate, channels, dtype):
    return AudioSample(generate_audio_data(samplerate, channels, dtype), samplerate, 0)


class TestData(unittest.TestCase):
    def test_colors(self):
        for fmt in [RGB, BGR]:
            data = np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8)
            data2 = fmt.format_to_cv2(fmt.cv2_to_format(data))
            self.assertTrue(
                np.all(np.isclose(data, data2, 1.0)), f"checking format {fmt}"
            )

    def test_resolve_device(self):
        self.assertEqual(
            resolve_device(Path("test.jpg")), str(Path("test.jpg").absolute())
        )
        self.assertEqual(
            resolve_device("file://path/to/test.jpg"),
            str(Path("path/to/test.jpg").absolute()),
        )
        self.assertEqual(
            resolve_device("http://camera-ip.org/image.jpg"),
            "http://camera-ip.org/image.jpg",
        )
        self.assertEqual(
            resolve_device("rtsp://camera-ip.org/image.jpg"),
            "rtsp://camera-ip.org/image.jpg",
        )
        self.assertEqual(resolve_device(0), 0)

    def test_image_save(self):
        with TemporaryDirectory() as dir:
            sample = ImageSample(
                np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8), 0, RGB
            )
            for fmt in ["jpg", "png"]:
                name = f"sample.{fmt}"
                sample.save(os.path.join(dir, name))
                sample.save(Path(dir, name))

    def test_image_save_load(self):
        with TemporaryDirectory() as dir:
            sample = ImageSample(
                np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8), 0, RGB
            )
            sample.save(Path(dir, "sample.png"))
            samples = ImageFolder(dir, RGB)
            self.assertTrue(np.allclose(sample.data, samples[0].data))

    def test_audio_save(self):
        test_formats = ["wav", "flac"]
        test_samplerates = [22050, 44100, 48000]
        test_channels = [1, 2]
        test_dtypes = [np.float32, np.float64, np.int16, np.int32]

        for format, samplerate, channels, dtype in product(
            test_formats, test_samplerates, test_channels, test_dtypes
        ):
            name = f"sample.{format}"
            with TemporaryDirectory() as dir:
                sample = generate_audio_sample(
                    samplerate, channels=channels, dtype=dtype
                )
                # test saving as any PathLike
                sample.save(os.path.join(dir, name))
                sample.save(Path(dir, name))

    def test_audio_save_load(self):
        test_formats = ["wav", "flac"]
        test_samplerates = [22050, 44100, 48000]
        test_channels = [1, 2]
        test_dtypes = [np.float32, np.float64]

        for format, samplerate, channels, dtype in product(
            test_formats, test_samplerates, test_channels, test_dtypes
        ):
            name = f"sample.{format}"
            with TemporaryDirectory() as dir:
                sample = generate_audio_sample(
                    samplerate, channels=channels, dtype=dtype
                )
                sample.save(Path(dir, name))
                samples = AudioFolder(dir)
                self.assertTrue(
                    np.allclose(sample.data, samples[0].data, atol=1e-4),
                    msg=f"failed: format={format} samplerate={samplerate} channels={channels} dtypes={dtype}",
                )

    def test_get_timestamp(self):
        ts = get_timestamp()
        self.assertIsInstance(ts, int)


if __name__ == "__main__":
    unittest.main()
