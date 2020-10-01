#!/usr/bin/env python3
# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import json
import logging
import os
import pika
import pika.exceptions
from threading import Thread, Lock
from queue import Queue, Empty
import time
import re
from typing import Any, NamedTuple, List


class PluginVersion(NamedTuple):
    major: int
    minor: int
    patch: int


class PluginConfig(NamedTuple):
    name: str
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
        name=os.environ.get('WAGGLE_PLUGIN_NAME', ''),
        id=int(os.environ.get('WAGGLE_PLUGIN_ID', 0)),
        version=parse_version_string(
            os.environ.get('WAGGLE_PLUGIN_VERSION', '0.0.0')),
        instance=int(os.environ.get('WAGGLE_PLUGIN_INSTANCE', 0)),
        node_id=os.environ.get('WAGGLE_NODE_ID', '0000000000000000'),
        sub_id=os.environ.get('WAGGLE_SUB_ID', '0000000000000000'),
        username=os.environ.get('WAGGLE_PLUGIN_USERNAME', 'plugin'),
        password=os.environ.get('WAGGLE_PLUGIN_PASSWORD', 'plugin'),
        host=os.environ.get('WAGGLE_PLUGIN_HOST', 'rabbitmq'),
        port=int(os.environ.get('WAGGLE_PLUGIN_PORT', 5672)),
    )

plugin_config = get_plugin_info_from_env()
plugin_running = False
plugin_lock = Lock()
outgoing_queue = Queue()
incoming_queue = Queue()


def init(name):
    global plugin_running
    with plugin_lock:
        if plugin_running:
            return
        Thread(target=publisher_main, daemon=True).start()
        plugin_running = True


def get(timeout=None):
    try:
        return json.loads(incoming_queue.get(timeout=timeout))
    except Empty:
        pass
    raise TimeoutError('plugin get timed out')


def subscribe(*topics):
    Thread(target=subscriber_main, args=topics, daemon=True).start()


def publish(msg):
    body = json.dumps({
        'ts': msg.get('ts') or time.time_ns(),
        'name': msg['name'],
        'value': msg['value'],
        'plugin': plugin_config.name,
    })

    outgoing_queue.put(body)


def publisher_main():
    connection_parameters = get_connection_parameters_for_config(plugin_config)

    while True:
        try:
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()
            publish_loop(channel)
        except pika.exceptions.AMQPConnectionError:
            continue
        except pika.exceptions.AMQPChannelError:
            continue


def publish_loop(channel):
    while True:
        try:
            body = outgoing_queue.get(timeout=30)
        except Empty:
            # TODO add a "heartbeat" to let server know we're still alive
            continue

        channel.basic_publish(
            exchange='to-validator',
            routing_key='',
            properties=pika.BasicProperties(
                delivery_mode=2,
                user_id=plugin_config.username),
            body=body)


def subscriber_main(*topics):
    connection_parameters = get_connection_parameters_for_config(plugin_config)

    while True:
        try:
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()
            queue = channel.queue_declare('', exclusive=True).method.queue
            for topic in topics:
                channel.queue_bind(queue, 'data.topic', topic)
            channel.basic_consume(queue, subscriber_callback, auto_ack=True)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            continue
        except pika.exceptions.AMQPChannelError:
            continue


def subscriber_callback(ch, method, properties, body):
    incoming_queue.put(body)


def get_connection_parameters_for_config(config):
    return pika.ConnectionParameters(
        host=config.host,
        port=config.port,
        credentials=pika.PlainCredentials(
            username=config.username,
            password=config.password,
        ),
        connection_attempts=100,
        socket_timeout=5.0,
    )
