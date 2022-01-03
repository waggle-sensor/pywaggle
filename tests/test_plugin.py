import unittest
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import time

from waggle.plugin import Plugin, PluginConfig, Uploader, raise_for_invalid_publish_name, get_timestamp
import wagglemsg


class TestPlugin(unittest.TestCase):

    def test_publish(self):
        with Plugin() as plugin:
            plugin.publish('test.int', 1)
            plugin.publish('test.float', 2.0)
            plugin.publish('test.bytes', b'three')
            plugin.publish('cows.total', 391, meta={
                "camera": "bottom_left",
            })
    
    def test_publish_check_reserved(self):
        with Plugin() as plugin:
            with self.assertRaises(ValueError):
                plugin.publish("upload", "path/to/data")

    def test_get(self):
        with Plugin() as plugin:
            plugin.subscribe('raw.#')
            with self.assertRaises(TimeoutError):
                plugin.get(timeout=0)
            with self.assertRaises(TimeoutError):
                plugin.get(timeout=0.001)

    def test_get_timestamp(self):
        ts = get_timestamp()
        self.assertIsInstance(ts, int)

    def test_raise_for_invalid_publish_name(self):
        with self.assertRaises(TypeError):
            raise_for_invalid_publish_name(None)
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name("")
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name(".")

        # check for reserved names
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name("upload")

        # use _ instead of -
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name("my-metric")
        # correct alternative
        raise_for_invalid_publish_name("my_metric")
        
        # assert len(name) <= 128
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name("x"*129)
        
        # no empty parts allowed
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name("vision.count..bird")
        # correct alternative
        raise_for_invalid_publish_name("vision.count.bird")

        # no spaces allowed
        with self.assertRaises(ValueError):
            raise_for_invalid_publish_name("sys.cpu temp")
        # correct alternative
        raise_for_invalid_publish_name("sys.cpu_temp")

    # TODO(sean) refactor messaging part to make testing this cleaner
    def test_upload_file(self):
        with TemporaryDirectory() as tempdir:
            pl = Plugin(PluginConfig(
                host="fake-rabbitmq-host",
                port=5672,
                username="plugin",
                password="plugin",
                app_id="0668b12c-0c15-462c-9e06-7239282411e5"
            ), uploader=Uploader(Path(tempdir, "uploads")))

            data = b'here some data in a data'
            upload_path = Path(tempdir, 'myfile.txt')
            upload_path.write_bytes(data)
            
            pl.upload_file(upload_path)
            item = pl.send.get_nowait()
            msg = wagglemsg.load(item.body)
            self.assertEqual(item.scope, "all")
            self.assertEqual(msg.name, "upload")
            self.assertIsNotNone(msg.timestamp)
            self.assertIsInstance(msg.value, str)
            self.assertIsNotNone(msg.meta)
            self.assertIn("filename", msg.meta)

    def test_timeit(self):
        with Plugin() as plugin:
            with plugin.timeit("dur"):
                time.sleep(0.001)
            item = plugin.send.get(0.01)
            msg = wagglemsg.load(item.body)
            self.assertEqual(msg.name, "dur")

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
