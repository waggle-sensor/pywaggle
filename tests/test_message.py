import unittest
import waggle.message as message

class TestMessage(unittest.TestCase):

    def test_message_invert(self):
        test_cases = [
            message.Message(
                name='env.temperature.htu21d',
                value=10,
                timestamp=1602704769215113000,
                meta={},
            ),
            message.Message(
                name='env.temperature.htu21d',
                value=21.2,
                timestamp=1602704769215113000,
                meta={},
            ),
            message.Message(
                name='env.temperature.htu21d',
                value=b'some binary data',
                timestamp=1602704769215113000,
                meta={},
            ),
            message.Message(
                name='env.temperature.htu21d',
                value='some string data',
                timestamp=1602704769215113000,
                meta={
                    "id": "meta-test-id"
                },
            )
        ]

        for msg in test_cases:
            out = message.load(message.dump(msg))
            self.assertEqual(msg, out)

if __name__ == '__main__':
    unittest.main()
