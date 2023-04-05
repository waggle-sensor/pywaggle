import unittest
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import time
from datetime import datetime
import os
import pika
import subprocess

from waggle.plugin import Plugin, PluginConfig, Uploader, get_timestamp
import wagglemsg

# TODO(sean) add integration testing against rabbitmq
# TODO(sean) clean up the queue interface. it would be better to not know about the plugin.send / plugin.recv queues explicitly.


class TestPlugin(unittest.TestCase):
    def test_publish(self):
        with Plugin() as plugin:
            plugin.publish("test.int", 1)
            plugin.publish("test.float", 2.0)
            plugin.publish("test.str", "three")
            plugin.publish(
                "cows.total",
                391,
                meta={
                    "camera": "bottom_left",
                },
            )

    def test_publish_check_reserved(self):
        with Plugin() as plugin:
            with self.assertRaises(ValueError):
                plugin.publish("upload", "path/to/data")

    def test_get(self):
        with Plugin() as plugin:
            plugin.subscribe("raw.#")
            with self.assertRaises(TimeoutError):
                plugin.get(timeout=0)
            with self.assertRaises(TimeoutError):
                plugin.get(timeout=0.001)

            msg = wagglemsg.Message("test", 1.0, 0, {})
            plugin.recv.put(msg)
            msg2 = plugin.get(timeout=0)
            self.assertEqual(msg, msg2)

    def test_get_timestamp(self):
        ts = get_timestamp()
        self.assertIsInstance(ts, int)

    def test_valid_values(self):
        with Plugin() as plugin:
            plugin.publish("test", 1)
            plugin.publish("test", 1.3)
            plugin.publish("test", "some string")
            with self.assertRaises(TypeError):
                plugin.publish("test", b"some bytes")
            with self.assertRaises(TypeError):
                plugin.publish("test", [1, 2, 3])
            with self.assertRaises(TypeError):
                plugin.publish("test", {1: 1, 2: 2, 3: 3})

    def test_valid_meta(self):
        with Plugin() as plugin:
            plugin.publish("test", 1, meta={"k": "v"})
            with self.assertRaises(TypeError):
                plugin.publish("test", 1, meta={"k": 10})
            with self.assertRaises(TypeError):
                plugin.publish("test", 1, meta={"k": 12.3})
            with self.assertRaises(TypeError):
                plugin.publish("test", 1, meta={"k": []})

    def test_valid_timestamp(self):
        with Plugin() as plugin:
            # valid int, nanosecond timestamp
            plugin.publish("test", 1, timestamp=1649694687904754000)

            # must prevent a float type timestamp
            ts = datetime(2022, 1, 1, 0, 0, 0).timestamp()
            with self.assertRaises(TypeError):
                plugin.publish("test", 1, timestamp=ts)

            # must prevent int timestamp in seconds from being loaded by flagging
            # timestamps that are too early.
            testcases = [
                datetime(2022, 1, 1, 0, 0, 0),
                datetime(3000, 1, 1, 0, 0, 0),
                datetime(5000, 1, 1, 0, 0, 0),
            ]

            for dt in testcases:
                with self.assertRaises(ValueError):
                    plugin.publish("test", 1, timestamp=int(dt.timestamp()))

    def test_valid_publish_names(self):
        with Plugin() as plugin:
            with self.assertRaises(TypeError):
                plugin.publish(None, 0)
            with self.assertRaises(ValueError):
                plugin.publish("", 0)
            with self.assertRaises(ValueError):
                plugin.publish(".", 0)

            # check for reserved names
            with self.assertRaises(ValueError):
                plugin.publish("upload", 0)

            # use _ instead of -
            with self.assertRaises(ValueError):
                plugin.publish("my-metric", 0)
            # correct alternative
            plugin.publish("my_metric", 0)

            # assert len(name) <= 128
            with self.assertRaises(ValueError):
                plugin.publish("x" * 129, 0)

            # no empty parts allowed
            with self.assertRaises(ValueError):
                plugin.publish("vision.count..bird", 0)
            # correct alternative
            plugin.publish("vision.count.bird", 0)

            # no spaces allowed
            with self.assertRaises(ValueError):
                plugin.publish("sys.cpu temp", 0)
            # correct alternative
            plugin.publish("sys.cpu_temp", 0)

    # TODO(sean) refactor messaging part to make testing this cleaner
    def test_upload_file(self):
        with TemporaryDirectory() as tempdir:
            pl = Plugin(
                PluginConfig(
                    host="fake-rabbitmq-host",
                    port=5672,
                    username="plugin",
                    password="plugin",
                    app_id="0668b12c-0c15-462c-9e06-7239282411e5",
                ),
                uploader=Uploader(Path(tempdir, "uploads")),
            )

            data = b"here some data in a data"
            upload_path = Path(tempdir, "myfile.txt")
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

            data = b"here some data in a data"

            upload_path = Path(tempdir, "myfile.txt")
            upload_path.write_bytes(data)

            path = uploader.upload_file(upload_path)
            self.assertFalse(upload_path.exists())

            self.assertEqual(data, Path(path, "data").read_bytes())
            meta = json.loads(Path(path, "meta").read_text())
            self.assertIn("timestamp", meta)
            self.assertIn("shasum", meta)
            self.assertEqual(meta["labels"]["filename"], upload_path.name)


def rabbitmq_available():
    try:
        subprocess.check_output(["docker-compose", "exec", "rabbitmq", "true"])
        return True
    except subprocess.CalledProcessError:
        return False


def get_admin_connection():
    params = pika.ConnectionParameters(
        credentials=pika.PlainCredentials("admin", "admin")
    )
    return pika.BlockingConnection(params)


@unittest.skipUnless(rabbitmq_available(), "rabbitmq not available")
class TestPluginWithRabbitMQ(unittest.TestCase):
    def setUp(self):
        os.environ["WAGGLE_PLUGIN_USERNAME"] = "plugin"
        os.environ["WAGGLE_PLUGIN_PASSWORD"] = "plugin"
        os.environ["WAGGLE_PLUGIN_HOST"] = "127.0.0.1"
        os.environ["WAGGLE_PLUGIN_PORT"] = "5672"

        with get_admin_connection() as conn, conn.channel() as ch:
            ch.queue_purge("to-validator")

    def test_publish(self):
        now = time.time_ns()

        with Plugin() as publisher:
            publisher.publish("test", 123, meta={"sensor": "bme680"}, timestamp=now)

        with get_admin_connection() as conn, conn.channel() as ch:
            _, _, body = ch.basic_get("to-validator", auto_ack=True)
            msg = wagglemsg.load(body)

        self.assertEqual(
            msg,
            wagglemsg.Message(
                name="test",
                value=123,
                meta={"sensor": "bme680"},
                timestamp=now,
            ),
        )

    def test_subscribe(self):
        msg = wagglemsg.Message(
            name="test",
            value=123,
            meta={"sensor": "bme680"},
            timestamp=time.time_ns(),
        )

        with Plugin() as subscriber:
            subscriber.subscribe("test")
            time.sleep(1)

            with get_admin_connection() as conn, conn.channel() as ch:
                ch.basic_publish("data.topic", "test", wagglemsg.dump(msg))

            msg2 = subscriber.get(1)
            self.assertEqual(msg, msg2)


class TestPluginLogDir(unittest.TestCase):
    def test_log_dir(self):
        import sage_data_client

        with TemporaryDirectory() as dir:
            dir = Path(dir)

            # create dummy upload file
            upload_file = Path(dir, "hello.txt")
            upload_file.write_text("hello")

            timestamp = get_timestamp()

            # set env var and run plugin
            try:
                os.environ["PYWAGGLE_LOG_DIR"] = str(dir)
                with Plugin() as plugin:
                    plugin.publish("test", 123, timestamp=timestamp)
                    plugin.publish(
                        "test.with.meta",
                        456,
                        meta={"user": "data"},
                        timestamp=timestamp + 10000,
                    )
                    plugin.upload_file(upload_file, timestamp=timestamp + 20000)
            finally:
                del os.environ["PYWAGGLE_LOG_DIR"]

            df = sage_data_client.load(Path(dir, "data.ndjson"))

            # ensure records match what was published
            self.assertEqual(len(df), 3)

            # TODO(sean) test timestamps
            self.assertEqual(df.loc[0, "name"], "test")
            self.assertEqual(df.loc[0, "value"], 123)

            self.assertEqual(df.loc[1, "name"], "test.with.meta")
            self.assertEqual(df.loc[1, "value"], 456)
            self.assertEqual(df.loc[1, "meta.user"], "data")

            self.assertEqual(df.loc[2, "name"], "upload")
            self.assertEqual(df.loc[2, "meta.filename"], "hello.txt")

            # ensure all uploads exist
            for path in df[df.name == "upload"].value:
                self.assertTrue(Path(path).exists())


def assertDictContainsSubset(t, a, b):
    t.assertLessEqual(a.items(), b.items())


if __name__ == "__main__":
    unittest.main()
