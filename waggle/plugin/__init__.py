#!/usr/bin/env python3
"""
This module provides an easy way to integrate sensor code into the Waggle data
pipeline as a plugin.

Plugins provide a standard interface to publishing data and processing
messages. The current API can be broken down into a few core areas:

Publishing:

* plugin.add_measurement(measument)
* plugin.publish_measurements()
* plugin.clear_measurements()

Example:

```
import waggle.plugin

# Initialize our plugin.
plugin = waggle.plugin.PrintPlugin()

# Add measurements to batch.
plugin.add_measurement({'sensor_id': 1, 'parameter_id': 0, 'value': 1})
plugin.add_measurement({'sensor_id': 1, 'parameter_id': 1, 'value': 2})
plugin.add_measurement({'sensor_id': 2, 'parameter_id': 0, 'value': 3})

# Publish the batch.
plugin.publish_measurements()
```

"""
import configparser
import logging
import os
import sys
import pika
import pika.credentials
import ssl
import waggle.protocol


def load_package_configs(*filenames):
    program_path = os.path.abspath(sys.argv[0])
    plugin_dir = os.path.dirname(os.path.dirname(program_path))

    config = configparser.ConfigParser()

    for filename in filenames:
        config.read(os.path.join(plugin_dir, filename))

    return config


def parse_version_string(s):
    if isinstance(s, tuple):
        return s
    return tuple(int(x) for x in s.split('.', 2))


def load_package_plugin_config():
    config = load_package_configs('plugin.ver', 'plugin.instance')
    section = config['plugin']

    return {
        'name': section.get('name'),
        'description': section.get('description'),
        'reference': section.get('reference'),
        'id': section.getint('id'),
        'version': parse_version_string(section.get('version')),
        'instance': section.getint('instance'),
    }


# probably can just turn Credentials into dictionary too... That would be
# more consistent.
def load_package_plugin_credentials():
    config = load_package_configs('plugin.credentials')
    section = config['credentials']

    return Credentials(
        host=section.get('host'),
        port=section.getint('port'),
        username=section.get('username'),
        password=section.get('password'),
        cacertfile=section.get('cacertfile'),
        certfile=section.get('certfile'),
        keyfile=section.get('keyfile'),
    )


def load_plugin_config(**kwargs):
    plugin_config = {
        'id': 0,
        'version': (0, 0, 0),
        'instance': 0,
    }

    plugin_config.update(load_package_configs('plugin.ver', 'plugin.instance')['plugin'])
    plugin_config.update(kwargs)
    return plugin_config


def get_connection_parameters(c):
    if c.cacertfile:
        return get_ssl_connection_parameters(c)
    return get_plain_connection_parameters(c)


def get_plain_connection_parameters(c):
    credentials = pika.credentials.PlainCredentials(
        username=c.username,
        password=c.password)

    return pika.ConnectionParameters(
        host=c.host,
        port=c.port,
        credentials=credentials)


def get_ssl_connection_parameters(c):
    return pika.ConnectionParameters(
        host=c.host,
        port=c.port,
        credentials=pika.credentials.ExternalCredentials(),
        ssl=True,
        ssl_options={
            'ca_certs': os.path.abspath(c.cacertfile),
            'keyfile': os.path.abspath(c.keyfile),
            'certfile': os.path.abspath(c.certfile),
            'cert_reqs': ssl.CERT_REQUIRED,
        })


def format_device_id(s):
    return s.rjust(16, '0')


class Credentials:

    def __init__(self, **kwargs):
        # we'll leave these out for now. in all cases, our system will validate
        # them.
        self.node_id = format_device_id(kwargs.get('node_id') or '0')
        self.sub_id = format_device_id(kwargs.get('sub_id') or '0')

        self.host = kwargs.get('host') or 'localhost'
        self.port = kwargs.get('port') or 23181

        # TODO Main use of derived use case is getting username from cert
        # Could later just directly extract from cert.
        # Then, even better, we can just use these credentials universally and
        # only have one connection system for RabbitMQ.
        self.username = kwargs.get('username') or 'node-{}'.format(self.node_id)
        self.password = kwargs.get('password')

        self.cacertfile = kwargs.get('cacert')
        self.certfile = kwargs.get('cert')
        self.keyfile = kwargs.get('key')


class Plugin:
    """
    Implements the plugin interface using a local RabbitMQ broker for the messaging layer.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger('pipeline.Plugin')

        plugin_config = load_plugin_config(**kwargs)
        self.plugin_id = plugin_config['id']
        self.plugin_version = parse_version_string(plugin_config['version'])
        self.plugin_instance = plugin_config['instance']

        print('plugin_id', self.plugin_id)
        print('plugin_version', self.plugin_version)
        print('plugin_instance', self.plugin_instance)

        self.credentials = kwargs.get('credentials')

        if self.credentials is None:
            self.credentials = load_package_plugin_credentials()

        self.queue = 'to-{}'.format(self.credentials.username)

        connection_parameters = get_connection_parameters(self.credentials)
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()

        self.measurements = []

    def publish(self, body):
        self.logger.debug('Publishing message data %s.', body)

        self.channel.basic_publish(
            exchange='messages',
            routing_key='',
            properties=pika.BasicProperties(
                delivery_mode=2,
                user_id=self.credentials.username),
            body=body)

    def get_waiting_messages(self):
        self.channel.queue_declare(queue=self.queue, durable=True)

        while True:
            method, properties, body = self.channel.basic_get(queue=self.queue)

            if body is None:
                break

            self.logger.debug('Yielding message data %s.', body)
            yield body

            self.logger.debug('Acking message data.')
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def add_measurement(self, sensorgram):
        """Add a measument to measurement queue.

        This function accepts both dict and bytes type objects.

        dict objects support the following keys:
        sensor_id -- sensor ID
        parameter_id -- parameter ID
        value -- raw sensor value bytes
        sensor_instance -- sensor instance (default 0)
        timestamp -- time measurement was taken (default now in seconds)

        These objects will be packed and added to the publishing buffer upon
        calling this function.

        Example:
        plugin.add_measurement({
            'sensor_id': 2,
            'parameter_id': 3,
            'value': b'some register values',
        })

        bytes objects should be in the standard packed sensorgram format. These
        will be published without modification.

        Example:
        data = read_sensorgram_bytes_from_serial_port()
        plugin.add_measurement(data)
        """
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        """Clear measurement queue without publishing."""
        self.measurements.clear()

    def publish_measurements(self):
        """Publish and clear the measurement queue."""
        message = waggle.protocol.pack_message({
            'sender_id': self.credentials.node_id,
            'sender_sub_id': self.credentials.sub_id,
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.plugin_id,
                'plugin_major_version': self.plugin_version[0],
                'plugin_minor_version': self.plugin_version[1],
                'plugin_patch_version': self.plugin_version[2],
                'plugin_instance': self.plugin_instance,
                'body': b''.join(self.measurements)
            })
        })

        self.publish(message)
        self.clear_measurements()

    def publish_heartbeat(self):
        pass


class PrintPlugin:
    """
    Implements the plugin interface and prints resutls to console. This class
    is intended for development and testing of plugin code.
    """

    def __init__(self, id, version, instance=0, credentials=None):
        self.plugin_id = id
        self.plugin_version = version
        self.plugin_instance = instance
        self.measurements = []
        self.process_callback = default_test_callback

    def publish(self, body):
        print('publish:')
        print(body)

    def get_waiting_messages(self):
        return

    def add_measurement(self, sensorgram):
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        """Clear measurement queue without publishing."""
        self.measurements.clear()

    def publish_measurements(self):
        """Publish and clear the measurement queue."""
        message = waggle.protocol.unpack_message(waggle.protocol.pack_message({
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.plugin_id,
                'plugin_major_version': self.plugin_version[0],
                'plugin_minor_version': self.plugin_version[1],
                'plugin_patch_version': self.plugin_version[2],
                'plugin_instance': self.plugin_instance,
                'body': b''.join(self.measurements)
            })
        }))

        datagram = waggle.protocol.unpack_datagram(message['body'])
        sensorgrams = waggle.protocol.unpack_sensorgrams(datagram['body'])

        self.process_callback(message, sensorgrams)
        self.clear_measurements()

    def publish_heartbeat(self):
        print('publish heartbeat')

    def process_measurements(self, process_callback):
        # NOTE Eventually wrap callback and make compatible
        # with a raw process_messages version.
        self.process_callback = process_callback

    def start_processing(self):
        pass


def default_test_callback(message, sensorgrams):
    print('message:')
    print(message)

    print('measurements:')

    for sensorgram in sensorgrams:
        print(sensorgram)


def pack_measurement(sensorgram):
    if isinstance(sensorgram, (bytes, bytearray)):
        return sensorgram
    if isinstance(sensorgram, dict):
        return waggle.protocol.pack_sensorgram(sensorgram)
    raise ValueError('Sensorgram must be bytes or dict.')


if __name__ == '__main__':
    plugin = PrintPlugin()

    def my_callback(message, sensorgrams):
        print('---')
        print(sensorgrams)

    plugin.process_measurements(my_callback)

    plugin.add_measurement({'sensor_id': 1, 'parameter_id': 0, 'value': 23.1})
    plugin.add_measurement({'sensor_id': 1, 'parameter_id': 1, 'value': 23.3})
    plugin.publish_measurements()
