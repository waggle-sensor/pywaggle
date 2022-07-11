from waggle.plugin import Plugin
import wagglemsg
import os
import pika
import time
import unittest

os.environ["WAGGLE_PLUGIN_USERNAME"] = "plugin"
os.environ["WAGGLE_PLUGIN_PASSWORD"] = "plugin"
os.environ["WAGGLE_PLUGIN_HOST"] = "127.0.0.1"
os.environ["WAGGLE_PLUGIN_PORT"] = "5672"


def get_admin_connection():
    params = pika.ConnectionParameters(credentials=pika.PlainCredentials("admin", "admin"))
    return pika.BlockingConnection(params)


class TestPlugin(unittest.TestCase):

    def setUp(self):
        with get_admin_connection() as conn, conn.channel() as ch:
            ch.queue_purge("to-validator")
    
    def test_publish(self):
        now = time.time_ns()

        with Plugin() as publisher:
            publisher.publish("test", 123, meta={"sensor": "bme680"}, timestamp=now)

        with get_admin_connection() as conn, conn.channel() as ch:
            _, _, body = ch.basic_get("to-validator", auto_ack=True)
            msg = wagglemsg.load(body)
        
        self.assertEqual(msg, wagglemsg.Message(
            name="test",
            value=123,
            meta={"sensor": "bme680"},
            timestamp=now,
        ))

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


if __name__ == "__main__":
    unittest.main()
