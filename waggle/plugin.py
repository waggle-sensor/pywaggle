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
from threading import Thread, Lock, Event
from queue import Queue, Empty, Full
import time
import re
from typing import Any, NamedTuple, List, Tuple
from base64 import b64encode
from pathlib import Path
import hashlib
from io import BytesIO
from secrets import token_hex

logger = logging.getLogger(__name__)
# turn down pika's logger automatically. by default, it's very verbose.
logging.getLogger('pika').setLevel(logging.CRITICAL)


# this wrapper around to distinguish ndarray from other types
class Image:

    def __init__(self, data):
        self.data = data


def convert_numpy_image_to_png(a):
    from PIL import Image
    from io import BytesIO
    import numpy as np
    img = Image.fromarray(np.uint8(a), 'RGB')
    with BytesIO() as buf:
        img.save(buf, 'png')
        return buf.getvalue()


def convert_png_to_numpy_image(a):
    raise NotImplementedError()


# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy 
try:
    from time import time_ns
except ImportError:
    def time_ns():
        return int(time.time() * 1e9)


class Message(NamedTuple):
    name: str
    value: Any
    timestamp: int
    src: str = ''
    dst: str = ''


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
plugin_running = Event()
outgoing_queue = Queue(64)
incoming_queue = Queue(64)
subscribe_queue = Queue(64)
data = DataStore()


def init():
    if not plugin_running.is_set():
        plugin_running.set()
        logger.debug('starting plugin worker thread')
        Thread(target=rabbitmq_worker_main, daemon=True).start()


def stop():
    logger.debug('stopping plugin worker thread')
    plugin_running.clear()


def get(timeout=None):
    try:
        return incoming_queue.get(timeout=timeout)
    except Empty:
        pass
    raise TimeoutError('plugin get timed out')


def subscribe(*topics):
    subscribe_queue.put(topics)


def publish(name, value, timestamp=None, scope=None, timeout=None):
    if timestamp is None:
        timestamp = time_ns()
    if scope is None:
        scope = 'all'
    msg = Message(
        name=name,
        value=value,
        timestamp=timestamp,
        src=plugin_config.name)
    logger.debug('adding message to outgoing queue: %s', msg)
    outgoing_queue.put((scope, msg), timeout=timeout)


class Uploader:

    def __init__(self, root):
        self.root = root

    def upload(self, obj):
        # get timestamp *before* any other work
        timestamp = time_ns()

        # wrap bytes-like objects as file-like object for convinience
        if isinstance(obj, (bytes, bytearray)):
            obj = BytesIO(obj)

        # first, we stage data and metadata in temp files
        random_name = token_hex(20)
        data_temp = Path(self.root, f'{random_name}.tmp')
        meta_temp = Path(self.root, f'{random_name}.meta.tmp')

        # ensure staging directory exists
        self.root.mkdir(parents=True, exist_ok=True)

        sha1 = hashlib.sha1()
        write_and_hash_file(data_temp, obj, sha1)
        checksum = sha1.hexdigest()

        meta = {
            'timestamp': timestamp,
            'sha1sum': checksum,
        }

        with meta_temp.open('w') as f:
            json.dump(meta, f, separators=(',', ':'))

        # atomically rename temp files
        name = f'{timestamp}-{checksum}'
        data_temp.rename(Path(self.root, name))
        meta_temp.rename(Path(self.root, name+'.meta'))

        # atomically move temp files
        # TODO decide if we should bundle into single directory like
        # * upload_id/data <- contains data
        # * upload_id/meta <- contains metadata
        # * ...?


def write_and_hash_file(path, obj, h):
    with path.open('wb') as f:
        while True:
            chunk = obj.read(32768)
            if len(chunk) == 0:
                break
            h.update(chunk)
            f.write(chunk)


uploader = Uploader(Path('/run/waggle/uploads'))
upload = uploader.upload


def rabbitmq_worker_main():
    # create connection parameters from config
    connection_parameters = pika.ConnectionParameters(
        host=plugin_config.host,
        port=plugin_config.port,
        credentials=pika.PlainCredentials(
            username=plugin_config.username,
            password=plugin_config.password,
        ),
        connection_attempts=100,
        socket_timeout=5.0,
    )

    # main loop. should run until closed and automatically recover
    # from rabbitmq related errors. 
    while plugin_running.is_set():
        try:
            logger.debug('connecting to rabbitmq broker at %s:%d with username "%s"',
                connection_parameters.host, connection_parameters.port,
                connection_parameters.credentials.username)
            with pika.BlockingConnection(connection_parameters) as connection:
                logger.debug('connected to rabbitmq broker')
                with connection.channel() as channel:
                    rabbitmq_worker_loop(connection, channel)
        except pika.exceptions.AMQPConnectionError:
            pass
        except pika.exceptions.AMQPChannelError:
            pass
        logger.debug('lost connection to rabbitmq broker')


def rabbitmq_worker_loop(connection, channel):
    def subscriber_callback(ch, method, properties, body):
        try:
            msg = amqp_to_message(properties, body)
        except TypeError:
            logger.debug('unsupported message type: %s %s', properties, body)
            return
        data[msg.name] = msg
        try:
            incoming_queue.put_nowait(msg)
            logger.debug('add message to incoming queue: %s', msg)
        except Full:
            logger.debug('incoming queue full - dropping message: %s', msg)
    
    def process_subscribe_queue():
        while plugin_running.is_set():
            try:
                topics = subscribe_queue.get_nowait()
            except Empty:
                break
            for topic in topics:
                logger.debug('subscribing to topic "%s"', topic)
                channel.queue_bind(queue, 'data.topic', topic)
    
    def process_publish_queue():
        while plugin_running.is_set():
            try:
                scope, msg = outgoing_queue.get_nowait()
            except Empty:
                break
            properties, body = message_to_amqp(msg)
            logger.debug('publishing message to rabbitmq: %s', msg)
            channel.basic_publish(
                exchange='to-validator',
                routing_key=scope,
                properties=properties,
                body=body)

    def process_queues_and_events():
        process_subscribe_queue()
        process_publish_queue()
        if plugin_running.is_set():
            connection.call_later(0.001, process_queues_and_events)
        else:
            logger.debug('stopping rabbitmq processing loop')
            channel.stop_consuming()

    # setup subscriber queue and bind
    queue = channel.queue_declare('', exclusive=True).method.queue
    channel.basic_consume(queue, subscriber_callback, auto_ack=True)
    # setup periodic publish and subscribe to topic checks
    connection.call_later(0.001, process_queues_and_events)
    logger.debug('starting rabbitmq processing loop')
    channel.start_consuming()


def message_to_amqp(msg: Message) -> Tuple[pika.BasicProperties, bytes]:
    # pack metadata into standard amqp message properties
    properties = pika.BasicProperties(
        delivery_mode=2,
        type=msg.name,
        timestamp=msg.timestamp,
        reply_to=msg.src)

    # determine content type
    if isinstance(msg.value, (bytes, bytearray)):
        body = msg.value
    elif isinstance(msg.value, Image):
        # encode as png to send as raw bytes
        properties.content_type = 'image/png'
        body = convert_numpy_image_to_png(msg.value.data)
    else:
        # attempt to encode all other types as compact json blob
        properties.content_type = 'application/json'
        body = json.dumps(msg.value, separators=(',', ':')).encode()

    return properties, body


def amqp_to_message(properties: pika.BasicProperties, body: bytes) -> Message:
    if properties.content_type is None:
        value = body
    elif properties.content_type == 'application/json':
        value = json.loads(body)
    else:
        raise TypeError('unsupported message type')

    return Message(
        name=properties.type,
        value=value,
        timestamp=properties.timestamp,
        src=properties.reply_to)


if __name__ == '__main__':
    u = Uploader(Path('./testdata'))
    u.upload(b'hello')
