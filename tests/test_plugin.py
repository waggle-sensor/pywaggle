import unittest
import time
import waggle.plugin as plugin
from waggle.plugin import Uploader
import shutil
from pathlib import Path
import json

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

class TestUploader(unittest.TestCase):

    def test_upload(self):
        shutil.rmtree('.testdata', ignore_errors=True)

        uploader = Uploader('.testdata')

        data = b'testdata'
        labels = {'name': 'example label'}
        path = uploader.upload(b'testdata', labels=labels)

        self.assertEqual(data, Path(path, 'data').read_bytes())
        meta = json.loads(Path(path, 'meta').read_text())
        self.assertIn('timestamp', meta)
        self.assertIn('shasum', meta)
        self.assertIn('labels', meta)
        self.assertDictEqual(labels, meta['labels'])

        shutil.rmtree('.testdata', ignore_errors=True)
    
    def test_upload_file(self):
        shutil.rmtree('.testdata', ignore_errors=True)

        uploader = Uploader('.testdata')

        data = b'here some data in a data'
        upload_path = Path('.myfile.txt')

        upload_path.write_bytes(data)
        path = uploader.upload_file(upload_path)
        self.assertFalse(upload_path.exists())

        self.assertEqual(data, Path(path, 'data').read_bytes())
        meta = json.loads(Path(path, 'meta').read_text())
        self.assertIn('timestamp', meta)
        self.assertIn('shasum', meta)
        self.assertEqual(meta['labels']['filename'], upload_path.name)

        shutil.rmtree('.testdata', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
