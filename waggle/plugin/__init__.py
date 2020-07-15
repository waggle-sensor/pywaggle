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
plugin.add_measurement({'id': 1, 'sub_id': 0, 'value': 1})
plugin.add_measurement({'id': 1, 'sub_id': 1, 'value': 2})
plugin.add_measurement({'id': 2, 'sub_id': 0, 'value': 3})

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
from threading import Thread
from queue import Queue
import time
import socket
from typing import NamedTuple
import re


class PluginVersion(NamedTuple):
    major: int
    minor: int
    patch: int


class PluginConfig(NamedTuple):
    id: int
    version: PluginVersion
    instance: int
    node_id: str
    sub_id: str
    username: str
    password: str
    host: str
    port: int


def parse_version_string(s: str) -> PluginVersion:
    m = re.match(r'(\d+)\.(\d+)\.(\d+)$', s)
    if m is None:
        raise ValueError(f'Invalid version string {s}.')
    return PluginVersion(
        major=int(m.group(1)),
        minor=int(m.group(2)),
        patch=int(m.group(3)))


def get_plugin_info_from_env() -> PluginConfig:
    return PluginConfig(
        id=int(os.environ.get('WAGGLE_PLUGIN_ID', 0)),
        version=parse_version_string(
            os.environ.get('WAGGLE_PLUGIN_VERSION', '0.0.0')),
        instance=int(os.environ.get('WAGGLE_PLUGIN_INSTANCE', 0)),
        node_id=os.environ.get('WAGGLE_NODE_ID', '0000000000000000'),
        sub_id=os.environ.get('WAGGLE_SUB_ID', '0000000000000000'),
        username=os.environ.get('WAGGLE_PLUGIN_USERNAME', 'worker'),
        password=os.environ.get('WAGGLE_PLUGIN_PASSWORD', 'worker'),
        host=os.environ.get('WAGGLE_PLUGIN_HOST', 'rabbitmq'),
        port=int(os.environ.get('WAGGLE_PLUGIN_PORT', '5672')),
    )


class Plugin:

    def __init__(self, **kwargs):
        self.logger = logging.getLogger('plugin.Plugin')
        self.logger.setLevel(logging.INFO)

        self.info = get_plugin_info_from_env()

        self.connection_parameters = pika.ConnectionParameters(
            host=os.environ.get('WAGGLE_PLUGIN_HOST', 'rabbitmq'),
            port=int(os.environ.get('WAGGLE_PLUGIN_PORT', '5672')),
            credentials=pika.credentials.PlainCredentials(
                username=self.info.username,
                password=self.info.password,
            ),
        )

        self.queue = 'to-{}'.format(self.info.username)

        self.measurements = []

        self.worker_queue = Queue()
        self.worker_thread = Thread(target=plugin_worker_main, args=(
            self, self.worker_queue), daemon=True)
        self.worker_thread.start()

    def publish(self, body):
        self.worker_queue.put(body)

    # def get_waiting_messages(self):
    #     raise NotImplementedError(
    #         'get_waiting_messages is not implemented yet')
    #     self.channel.queue_declare(queue=self.queue, durable=True)

    #     while True:
    #         method, _, body = self.channel.basic_get(queue=self.queue)

    #         if body is None:
    #             break

    #         self.logger.debug('yield message %s', method.delivery_tag)
    #         yield body

    #         self.logger.debug('ack message %s', method.delivery_tag)
    #         self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def add_measurement(self, sensorgram):
        self.logger.info('add measurement %s', sensorgram)
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        self.logger.debug('clear measurements')
        self.measurements.clear()

    def publish_measurements(self):
        message = waggle.protocol.pack_message({
            'sender_id': self.info.node_id,
            'sender_sub_id': self.info.sub_id,
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.info.id,
                'plugin_major_version': self.info.version.major,
                'plugin_minor_version': self.info.version.minor,
                'plugin_patch_version': self.info.version.patch,
                'plugin_instance': self.info.instance,
                'body': b''.join(self.measurements)
            })
        })

        self.publish(message)
        self.clear_measurements()

    def publish_message(self, receiver_id, receiver_sub_id, body):
        message = waggle.protocol.pack_message({
            'sender_id': self.info.id,
            'sender_sub_id': self.info.sub_id,
            'receiver_id': receiver_id,
            'receiver_sub_id': receiver_sub_id,
            'body': waggle.protocol.pack_datagram({
                'plugin_id': self.info.id,
                'plugin_major_version': self.info.version.major,
                'plugin_minor_version': self.info.version.minor,
                'plugin_patch_version': self.info.version.patch,
                'plugin_instance': self.info.instance,
                'body': body,
            })
        })

        self.publish(message)


def plugin_worker_main(plugin: Plugin, queue: Queue):
    logging.getLogger('pika').setLevel(logging.CRITICAL)

    while True:
        try:
            plugin_worker_connect_and_process(plugin, queue)
        except Exception:
            pass
        time.sleep(10)


def plugin_worker_connect_and_process(plugin: Plugin, queue: Queue):
    logger = logging.getLogger('plugin.worker')

    logger.info(f'connecting to rabbitmq...')

    try:
        connection = pika.BlockingConnection(plugin.connection_parameters)
    except socket.gaierror:
        logger.error('could not find rabbitmq host "%s"', plugin.info.host)
        return

    channel = connection.channel()
    logger.info('connected to rabbitmq')

    while True:
        body = queue.get()

        logger.debug('publishing to rabbitmq')

        channel.basic_publish(
            exchange='messages',
            routing_key='',
            properties=pika.BasicProperties(
                delivery_mode=2,
                user_id=plugin.info.username),
            body=body)


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
