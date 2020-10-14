import unittest
import time
import waggle.plugin as plugin

class TestPlugin(unittest.TestCase):

    def setUp(self):
        plugin.init()
    
    def tearDown(self):
        plugin.stop()

    def test_publish(self):
        plugin.publish('test.int', 1)
        plugin.publish('test.float', 2.0)
        plugin.publish('test.bytes', b'three')
    
    def test_get(self):
        plugin.subscribe('raw.#')
        with self.assertRaises(TimeoutError):
            plugin.get(timeout=0)
        with self.assertRaises(TimeoutError):
            plugin.get(timeout=0.001)

class TestMessage(unittest.TestCase):

    def test_message_invert(self):
        test_cases = [
            plugin.Message(
                name='env.temperature.htu21d',
                value=10,
                timestamp=1602704769215113000,
                sender='test:0.0.1',
            ),
            plugin.Message(
                name='env.temperature.htu21d',
                value=21.2,
                timestamp=1602704769215113000,
                sender='test:0.0.1',
            ),
            plugin.Message(
                name='env.temperature.htu21d',
                value=b'some binary data',
                timestamp=1602704769215113000,
                sender='test:0.0.1',
            ),
            plugin.Message(
                name='env.temperature.htu21d',
                value='some binary data',
                timestamp=1602704769215113000,
                sender='test:0.0.1',
            )
        ]

        for msg in test_cases:
            out = plugin.amqp_to_message(*plugin.message_to_amqp(msg))
            self.assertEqual(msg, out)

if __name__ == '__main__':
    unittest.main()
