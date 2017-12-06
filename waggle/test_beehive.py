import unittest
import ssl
from .beehive import build_connection_parameters
from .beehive import pack_message


class TestConnectionParameters(unittest.TestCase):

    def test_build_connection_parameters(self):
        config = {
            'host': 'myhost',
            'port': 12345,
            'vhost': 'myvhost',
            'username': 'myusername',
            'password': 'mypassword',
            'cacert': '/path/to/cacert',
        }

        parameters = build_connection_parameters(config)
        credentials = parameters.credentials
        ssl_options = parameters.ssl_options

        self.assertEqual(parameters.host, config['host'])
        self.assertEqual(parameters.port, config['port'])
        self.assertEqual(parameters.virtual_host, config['vhost'])

        self.assertEqual(credentials.username, config['username'])
        self.assertEqual(credentials.password, config['password'])

        self.assertTrue(parameters.ssl)
        self.assertEqual(ssl_options['cert_reqs'], ssl.CERT_REQUIRED)
        self.assertEqual(ssl_options['ca_certs'], config['cacert'])

        self.assertGreaterEqual(parameters.connection_attempts, 5)
        self.assertGreaterEqual(parameters.retry_delay, 5.0)
        self.assertGreaterEqual(parameters.socket_timeout, 10.0)

    def test_build_connection_require_cacert(self):
        config = {
            'host': 'myhost',
            'port': 12345,
            'vhost': 'myvhost',
            'username': 'myusername',
            'password': 'mypassword',
        }

        with self.assertRaisesRegex(KeyError, 'cacert'):
            build_connection_parameters(config)

    def test_build_connection_client_cert(self):
        config = {
            'host': 'myhost',
            'port': 12345,
            'vhost': 'myvhost',
            'username': 'myusername',
            'password': 'mypassword',
            'cacert': '/path/to/cacert',
            'cert': '/path/to/cert',
            'key': '/path/to/key',
        }

        parameters = build_connection_parameters(config)
        ssl_options = parameters.ssl_options

        self.assertEqual(ssl_options['certfile'], config['cert'])
        self.assertEqual(ssl_options['keyfile'], config['key'])


class TestMessage(unittest.TestCase):

    def test_pack_message(self):
        message = {
            'timestamp': 123456,
            'topic': 'sometopic',
            'body': b'this is a test',
        }

        internal = pack_message(message)

        self.assertEqual(internal['properties'].timestamp, message['timestamp'])
        self.assertEqual(internal['properties'].delivery_mode, 2)
        self.assertEqual(internal['body'], message['body'])