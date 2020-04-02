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


def parse_version_string(s):
    if isinstance(s, tuple):
        assert len(s) == 3
        return tuple(int(x) for x in s)
    return tuple(int(x) for x in s.split('.', 2))


class Plugin:
    """
    Implements the plugin interface using a local RabbitMQ broker for the messaging layer.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger('pipeline.Plugin')

        self.id = int(os.environ['WAGGLE_PLUGIN_ID'])
        self.version = parse_version_string(
            os.environ['WAGGLE_PLUGIN_VERSION'])
        self.instance = int(os.environ['WAGGLE_PLUGIN_INSTANCE'])

        self.node_id = os.environ['WAGGLE_NODE_ID']
        self.sub_id = os.environ['WAGGLE_SUB_ID']

        self.credentials = pika.credentials.PlainCredentials(
            username=os.environ['WAGGLE_PLUGIN_USERNAME'],
            password=os.environ['WAGGLE_PLUGIN_PASSWORD'],
        )

        self.connection_parameters = pika.ConnectionParameters(
            host=os.environ.get('WAGGLE_PLUGIN_HOST', 'rabbitmq'),
            port=int(os.environ.get('WAGGLE_PLUGIN_PORT', '5672')),
            credentials=self.credentials,
        )

        self.queue = 'to-{}'.format(self.credentials.username)
        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        self.measurements = []

    def publish(self, body):
        self.logger.debug('publish data %s', body)

        for i in range(2):
            try:
                self.channel.basic_publish(
                    exchange='messages',
                    routing_key='',
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        user_id=self.credentials.username),
                    body=body)
                break
            except pika.exceptions.ConnectionClosed:
                self.connect()
            except Exception:
                break

    def get_waiting_messages(self):
        self.channel.queue_declare(queue=self.queue, durable=True)

        while True:
            method, _, body = self.channel.basic_get(queue=self.queue)

            if body is None:
                break

            self.logger.debug('yield message %s', method.delivery_tag)
            yield body

            self.logger.debug('ack message %s', method.delivery_tag)
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def add_measurement(self, sensorgram):
        self.logger.debug('add measurement %s', sensorgram)
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        self.logger.debug('clear measurements')
        self.measurements.clear()

    def publish_measurements(self):
        message = waggle.protocol.pack_message({
            'sender_id': self.node_id,
            'sender_sub_id': self.sub_id,
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.id,
                'plugin_major_version': self.version[0],
                'plugin_minor_version': self.version[1],
                'plugin_patch_version': self.version[2],
                'plugin_instance': self.instance,
                'body': b''.join(self.measurements)
            })
        })

        self.publish(message)
        self.clear_measurements()

    def publish_message(self, receiver_id, receiver_sub_id, body):
        message = waggle.protocol.pack_message({
            'sender_id': self.id,
            'sender_sub_id': self.sub_id,
            'receiver_id': receiver_id,
            'receiver_sub_id': receiver_sub_id,
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.id,
                'plugin_major_version': self.version[0],
                'plugin_minor_version': self.version[1],
                'plugin_patch_version': self.version[2],
                'plugin_instance': self.instance,
                'body': body,
            })
        })

        self.publish(message)

    def publish_heartbeat(self):
        pass


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


def encode_for_channel(x):
    if isinstance(x, bytes):
        return encode_bytes(x)
    if isinstance(x, list):
        return ','.join(encode_for_channel(xi) for xi in x)
    if isinstance(x, bool):
        return str(int(x))
    return str(x)


def start_processing_measurements(handler, reader=sys.stdin.buffer, writer=sys.stdout):
    results = []

    for message, datagram, sensorgram in measurements_in_message_data(reader.read()):
        for r in handler(message, datagram, sensorgram):
            r['timestamp'] = sensorgram['timestamp']
            r['value_raw'] = encode_for_channel(r['value_raw'])
            r['value_hrf'] = encode_for_channel(r['value_hrf'])
            results.append(r)

    json.dump(results, writer, separators=(',', ':'))
