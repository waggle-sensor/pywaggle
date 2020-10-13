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
from queue import Queue, Empty, Full
import time
import re
from typing import Any, NamedTuple, List
from hashlib import sha1
from base64 import b64encode


class Image:

    def __init__(self, data):
        self.data = data


def convert_numpy_image_to_png(a):
    from PIL import Image
    from io import BytesIO
    import numpy as np
    
    # normalize data to [0, 255]
    a = a - a.min()
    max = a.max()
    if max > 0:
        a /= max * 255
    a = np.uint8(a)

    img = Image.fromarray(a, 'RGB')

    with BytesIO() as buf:
        img.save(buf, 'png')
        return buf.getvalue()


# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy 
def fallback_time_ns():
    return int(time.time() * 1e9)

try:
    from time import time_ns
except ImportError:
    time_ns = fallback_time_ns

class Value:
    name: str
    value: Any
    timestamp: int

    def __init__(self, name, value, timestamp=None):
        self.name = name
        self.value = value
        self.timestamp = timestamp or time_ns()
    
    def __str__(self):
        return '<{} {} @ {}>'.format(self.name, self.value, self.timestamp)


class PluginVersion(NamedTuple):
    major: int
    minor: int
    patch: int


class PluginConfig(NamedTuple):
    name: str
    id: int
    version: PluginVersion
    instance: int
    username: str
    password: str
    host: str
    port: int


class DataStore:

    def __init__(self):
        self.lock = Lock()
        self.data = {}

    def get(self, name):
        with self.lock:
            return self.data.get(name)

    def __getitem__(self, name):
        with self.lock:
            return self.data[name]
        
    def __setitem__(self, name, value):
        with self.lock:
            self.data[name] = value

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
        username=os.environ.get('WAGGLE_PLUGIN_USERNAME', 'plugin'),
        password=os.environ.get('WAGGLE_PLUGIN_PASSWORD', 'plugin'),
        host=os.environ.get('WAGGLE_PLUGIN_HOST', 'rabbitmq'),
        port=int(os.environ.get('WAGGLE_PLUGIN_PORT', 5672)),
    )

plugin_config = get_plugin_info_from_env()
plugin_running = False
plugin_lock = Lock()
outgoing_queue = Queue(64)
incoming_queue = Queue(64)
data = DataStore()

def init():
    global plugin_running
    with plugin_lock:
        if plugin_running:
            return
        Thread(target=publisher_main, daemon=True).start()
        plugin_running = True


def get(timeout=None):
    try:
        return incoming_queue.get(timeout=timeout)
    except Empty:
        pass
    raise TimeoutError('plugin get timed out')


def subscribe(*topics):
    Thread(target=subscriber_main, args=topics, daemon=True).start()


def publish(name, value, timestamp=None, scope=None):
    if timestamp is None:
        timestamp = time_ns()
    if scope is None:
        scope = ['node', 'beehive']

    msg = {
        'ts': timestamp,
        'name': name,
        'scope': scope,
        'plugin': plugin_config.name,
    }

    if isinstance(value, Image):
        value = convert_numpy_image_to_png(value.data)
        value = b64encode(value).decode()
        msg['value'] = value
        msg['enc'] = 'png'
    elif isinstance(value, (bytes, bytearray)):
        value = b64encode(value).decode()
        msg['value'] = value
        msg['enc'] = 'b64'
    else:
        msg['value'] = value

    body = json.dumps(msg)

    try:
        outgoing_queue.put_nowait(body)
        return
    except Full:
        pass

    try:
        outgoing_queue.get_nowait()
    except Empty:
        pass

    try:
        outgoing_queue.put_nowait(body)
    except Full:
        pass


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
    try:
        msg = json.loads(body)
    except json.JSONDecodeError:
        return

    obj = Value(msg['name'], msg['value'], msg['ts'])
    data[obj.name] = obj

    # attempt to add new item to incoming queue
    try:
        incoming_queue.put_nowait(obj)
        return
    except Full:
        pass

    # if incoming queue is full, remove oldest item and attempt to add new
    try:
        incoming_queue.get_nowait()
    except Empty:
        pass
    try:
        incoming_queue.put_nowait(obj)
    except Full:
        pass


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
