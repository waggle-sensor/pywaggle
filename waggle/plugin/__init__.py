#!/usr/bin/env python3
# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
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
import json
import configparser
import logging
import os
import sys
import pika
import pika.credentials
import ssl
import waggle.protocol
from base64 import b64encode


def load_package_configs(*filenames):
    program_path = os.path.abspath(sys.argv[0])
    plugin_dir = os.path.dirname(os.path.dirname(program_path))

    config = configparser.ConfigParser()

    for filename in filenames:
        config.read(os.path.join(plugin_dir, filename))

    return config


def parse_version_string(s):
    if isinstance(s, tuple):
        assert len(s) == 3
        return tuple(int(x) for x in s)
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
        cacertfile=section.get('cacert'),
        certfile=section.get('cert'),
        keyfile=section.get('key'),
        node_id=section.get('node_id'),
        sub_id=section.get('sub_id'),
    )


def load_plugin_config(**kwargs):
    plugin_config = {
        'instance': 0,
    }

    # attempt to load plugin config files
    try:
        plugin_config.update(load_package_plugin_config())
    except KeyError:
        pass

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
        host=c.host or 'localhost',
        port=c.port or 5672,
        credentials=credentials)


def get_ssl_connection_parameters(c):
    host = c.host or 'localhost'
    port = c.port or 23181

    context = ssl.create_default_context(
        cafile=os.path.abspath(c.cacertfile))

    context.load_cert_chain(
        os.path.abspath(c.certfile),
        os.path.abspath(c.keyfile))
    
    context.check_hostname = False
    
    ssl_options = pika.SSLOptions(context, host)

    return pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.credentials.ExternalCredentials(),
        ssl_options=ssl_options)


def format_device_id(s):
    return s.rjust(16, '0')


class Credentials:

    def __init__(self, **kwargs):
        # we'll leave these out for now. in all cases, our system will validate
        # them.
        self.node_id = format_device_id(kwargs.get('node_id') or '0000000000000000')
        self.sub_id = format_device_id(kwargs.get('sub_id') or '0000000000000000')

        self.host = kwargs.get('host')
        self.port = kwargs.get('port')

        # TODO Main use of derived use case is getting username from cert
        # Could later just directly extract from cert.
        # Then, even better, we can just use these credentials universally and
        # only have one connection system for RabbitMQ.
        self.username = kwargs.get('username') or 'node-{}'.format(self.node_id)
        self.password = kwargs.get('password')

        self.cacertfile = kwargs.get('cacert')
        self.certfile = kwargs.get('cert')
        self.keyfile = kwargs.get('key')


class PluginBase:

    def load_config(self, **kwargs):
        plugin_config = load_plugin_config(**kwargs)
        self.plugin_id = int(plugin_config['id'])
        self.plugin_version = parse_version_string(plugin_config['version'])
        self.plugin_instance = int(plugin_config['instance'])


class Plugin(PluginBase):
    """
    Implements the plugin interface using a local RabbitMQ broker for the messaging layer.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger('pipeline.Plugin')
        self.load_config(**kwargs)
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
            method, _, body = self.channel.basic_get(queue=self.queue)

            if body is None:
                break

            self.logger.debug('Yielding message data %s.', body)
            yield body

            self.logger.debug('Acking message data.')
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def add_measurement(self, sensorgram):
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        self.measurements.clear()

    def publish_measurements(self):
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

    def publish_message(self, receiver_id, receiver_sub_id, body):
        message = waggle.protocol.pack_message({
            'sender_id': self.credentials.node_id,
            'sender_sub_id': self.credentials.sub_id,
            'receiver_id': receiver_id,
            'receiver_sub_id': receiver_sub_id,
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.plugin_id,
                'plugin_major_version': self.plugin_version[0],
                'plugin_minor_version': self.plugin_version[1],
                'plugin_patch_version': self.plugin_version[2],
                'plugin_instance': self.plugin_instance,
                'body': body,
            })
        })

        self.publish(message)

    def publish_heartbeat(self):
        pass


class PrintPlugin(PluginBase):
    """
    Implements the plugin interface and prints resutls to console. This class
    is intended for development and testing of plugin code.
    """

    def __init__(self, **kwargs):
        self.load_config(**kwargs)
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


class PipePlugin(PluginBase):

    def __init__(self, **kwargs):
        self.load_config(**kwargs)
        self.measurements = []
        self.process_callback = default_test_callback

    def publish(self, body):
        sys.stdout.buffer.write(body)
        sys.stdout.buffer.flush()

    def get_waiting_messages(self):
        return

    def add_measurement(self, sensorgram):
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        """Clear measurement queue without publishing."""
        self.measurements.clear()

    def publish_measurements(self):
        """Publish and clear the measurement queue."""
        self.publish(waggle.protocol.pack_message({
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.plugin_id,
                'plugin_major_version': self.plugin_version[0],
                'plugin_minor_version': self.plugin_version[1],
                'plugin_patch_version': self.plugin_version[2],
                'plugin_instance': self.plugin_instance,
                'body': b''.join(self.measurements)
            })
        }))

        self.clear_measurements()

    def publish_heartbeat(self):
        pass

    def process_measurements(self, process_callback):
        self.process_callback = process_callback

    def start_processing(self):
        pass


def default_test_callback(message, sensorgrams):
    print('published measurements:')

    for sensorgram in sensorgrams:
        print(sensorgram)


def pack_measurement(sensorgram):
    if isinstance(sensorgram, (bytes, bytearray)):
        return sensorgram
    if isinstance(sensorgram, dict):
        return waggle.protocol.pack_sensorgram(sensorgram)
    raise ValueError('Sensorgram must be bytes or dict.')


def measurements_in_message_data(message_data):
    for message in waggle.protocol.unpack_messages(message_data):
        for datagram in waggle.protocol.unpack_datagrams(message['body']):
            for sensorgram in waggle.protocol.unpack_sensorgrams(datagram['body']):
                yield message, datagram, sensorgram


def encode_bytes(b):
    return b64encode(b).decode()


def stringify(x):
    if isinstance(x, bytes):
        return encode_bytes(x)
    if isinstance(x, list):
        return ','.join(stringify(xi) for xi in x)
    return str(x)


def start_processing_measurements(handler, reader=sys.stdin.buffer, writer=sys.stdout):
    results = []

    for message, datagram, sensorgram in measurements_in_message_data(reader.read()):
        for r in handler(message, datagram, sensorgram):
            r['timestamp'] = sensorgram['timestamp']
            r['value_raw'] = stringify(r['value_raw'])
            r['value_hrf'] = stringify(r['value_hrf'])
            results.append(r)

    json.dump(results, writer, separators=(',', ':'))


if __name__ == '__main__':
    plugin = PrintPlugin()

    def my_callback(message, sensorgrams):
        print('---')
        print(sensorgrams)

    plugin.process_measurements(my_callback)

    plugin.add_measurement({'sensor_id': 1, 'parameter_id': 0, 'value': 23.1})
    plugin.add_measurement({'sensor_id': 1, 'parameter_id': 1, 'value': 23.3})
    plugin.publish_measurements()
