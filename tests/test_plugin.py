import unittest
import waggle.plugin as plugin
from waggle.plugin import Uploader
import shutil
from pathlib import Path
import json
from tempfile import TemporaryDirectory

class TestPlugin(unittest.TestCase):

    def setUp(self):
        plugin.init()
    
    def tearDown(self):
        plugin.stop()

    def test_publish(self):
        plugin.publish('test.int', 1)
        plugin.publish('test.float', 2.0)
        plugin.publish('test.bytes', b'three')
        plugin.publish('cows.total', 391, meta={
            "camera": "bottom_left",
        })
    
    def test_get(self):
        plugin.subscribe('raw.#')
        with self.assertRaises(TimeoutError):
            plugin.get(timeout=0)
        with self.assertRaises(TimeoutError):
            plugin.get(timeout=0.001)

    def test_get_timestamp(self):
        ts = plugin.get_timestamp()
        self.assertIsInstance(ts, int)

    def test_raise_for_invalid_publish_name(self):
        with self.assertRaises(TypeError):
            plugin.raise_for_invalid_publish_name(None)
        with self.assertRaises(ValueError):
            plugin.raise_for_invalid_publish_name("")
        with self.assertRaises(ValueError):
            plugin.raise_for_invalid_publish_name(".")

        # use _ instead of -
        with self.assertRaises(ValueError):
            plugin.raise_for_invalid_publish_name("my-metric")
        # correct alternative
        plugin.raise_for_invalid_publish_name("my_metric")
        
        # assert len(name) <= 128
        with self.assertRaises(ValueError):
            plugin.raise_for_invalid_publish_name("x"*129)
        
        # no empty parts allowed
        with self.assertRaises(ValueError):
            plugin.raise_for_invalid_publish_name("vision.count..bird")
        # correct alternative
        plugin.raise_for_invalid_publish_name("vision.count.bird")

        # no spaces allowed
        with self.assertRaises(ValueError):
            plugin.raise_for_invalid_publish_name("sys.cpu temp")
        # correct alternative
        plugin.raise_for_invalid_publish_name("sys.cpu_temp")

class TestUploader(unittest.TestCase):
    
    def test_upload_file(self):
        with TemporaryDirectory() as tempdir:
            uploader = Uploader(Path(tempdir, "uploads"))

            data = b'here some data in a data'

            upload_path = Path(tempdir, 'myfile.txt')
            upload_path.write_bytes(data)
            
            path = uploader.upload_file(upload_path)
            self.assertFalse(upload_path.exists())

            self.assertEqual(data, Path(path, 'data').read_bytes())
            meta = json.loads(Path(path, 'meta').read_text())
            self.assertIn('timestamp', meta)
            self.assertIn('shasum', meta)
            self.assertEqual(meta['labels']['filename'], upload_path.name)


if __name__ == '__main__':
    unittest.main()
