import unittest
import shutil
import plugin
from plugin import Uploader
from pathlib import Path
import json


class TestUploader(unittest.TestCase):

    def test_plugin(self):
        plugin.init()
        plugin.subscribe('hello.topic')
        plugin.publish('env.temp', 1)
        plugin.publish('env.temp', 2)
        plugin.publish('env.temp', 3)
        plugin.stop()
        plugin.plugin.stopped.wait()

    def test_uploader(self):
        shutil.rmtree('.testdata', ignore_errors=True)

        uploader = Uploader('.testdata')

        data = b'testdata'
        labels = {'name': 'example label'}
        path = uploader.upload(b'testdata', **labels)

        self.assertEqual(data, Path(path, 'data').read_bytes())
        meta = json.loads(Path(path, 'meta').read_text())
        self.assertIn('timestamp', meta)
        self.assertIn('shasum', meta)
        self.assertIn('labels', meta)
        self.assertDictEqual(labels, meta['labels'])

        shutil.rmtree('.testdata', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
