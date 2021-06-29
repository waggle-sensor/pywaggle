#!/usr/bin/env python3
# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import waggle.message as message
import json
import logging
import base64
import os
import pika
import pika.exceptions
from threading import Thread, Lock, Event
from queue import Queue, Empty, Full
import time
import re
from typing import Any, NamedTuple, List, Tuple
from pathlib import Path
import hashlib
from io import BytesIO
from secrets import token_hex

logger = logging.getLogger(__name__)
# turn down pika's logger automatically. by default, it's very verbose.
logging.getLogger('pika').setLevel(logging.CRITICAL)


# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy 
try:
    from time import time_ns
except ImportError:
    def time_ns():
        return int(time.time() * 1e9)


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


class Plugin:

    def __init__(self, config):
        self.config = config

        self.connection_parameters = pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=pika.PlainCredentials(
                username=config.username,
                password=config.password,
            ),
            connection_attempts=1,
            socket_timeout=3.0,
        )

        self.running = Event()
        self.stopped = Event()

        self.outgoing_queue = Queue(64)
        self.incoming_queue = Queue(64)
        self.subscribe_queue = Queue(64)

    def init(self):
        logger.debug('starting plugin worker thread')
        Thread(target=self.run_rabbitmq_worker, daemon=True).start()

    def stop(self):
        logger.debug('stopping plugin worker thread')
        self.running.clear()

    def get(self, timeout=None):
        try:
            return self.incoming_queue.get(timeout=timeout)
        except Empty:
            pass
        raise TimeoutError('plugin get timed out')

    def subscribe(self, *topics):
        self.subscribe_queue.put(topics)

    def publish(self, name, value, timestamp=None, meta={}, scope=None, timeout=None):
        if timestamp is None:
            timestamp = time_ns()
        if scope is None:
            scope = 'all'
        msg = message.Message(name=name, value=value, timestamp=timestamp, meta=meta)
        logger.debug('adding message to outgoing queue: %s', msg)
        self.outgoing_queue.put((scope, msg), timeout=timeout)

    def run_rabbitmq_worker(self):
        if self.running.is_set():
            logger.warning('already have an instance of rabbitmq worker running')
            return

        try:
            self.running.set()
            self.stopped.clear()

            while self.running.is_set():
                try:
                    logger.debug('connecting to rabbitmq broker at %s:%d with username "%s"',
                                 self.connection_parameters.host,
                                 self.connection_parameters.port,
                                 self.connection_parameters.credentials.username)
                    with pika.BlockingConnection(self.connection_parameters) as connection:
                        logger.debug('connected to rabbitmq broker')
                        self.rabbitmq_worker_mainloop(connection)
                except Exception as exc:
                    logger.debug('rabbitmq connection error: %s', exc)
                time.sleep(1)
        finally:
            self.running.clear()
            self.stopped.set()

    def rabbitmq_worker_mainloop(self, connection):
        channel = connection.channel()

        def subscriber_callback(ch, method, properties, body):
            try:
                msg = message.load(body)
            except TypeError:
                logger.debug('unsupported message type: %s %s', properties, body)
                return
            try:
                self.incoming_queue.put_nowait(msg)
                logger.debug('add message to incoming queue: %s', msg)
            except Full:
                logger.debug('incoming queue full - dropping message: %s', msg)
        
        def process_subscribe_queue():
            while self.running.is_set():
                try:
                    topics = self.subscribe_queue.get_nowait()
                except Empty:
                    break
                for topic in topics:
                    logger.debug('subscribing to topic "%s"', topic)
                    channel.queue_bind(queue, 'data.topic', topic)

        def process_publish_queue():
            while self.running.is_set():
                try:
                    scope, msg = self.outgoing_queue.get_nowait()
                except Empty:
                    break
                properties = pika.BasicProperties(
                    delivery_mode=2,
                    user_id=self.connection_parameters.credentials.username)
                body = message.dump(msg)
                logger.debug('publishing message to rabbitmq: %s', msg)
                channel.basic_publish(
                    exchange='to-validator',
                    routing_key=scope,
                    properties=properties,
                    body=body)

        def process_queues_and_events():
            process_subscribe_queue()
            process_publish_queue()
            if self.running.is_set():
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


class Uploader:

    def __init__(self, root):
        self.root = Path(root)

    # NOTE uploads are stored in the following directory structure:
    # root/
    #   timestamp-sha1sum/
    #     data
    #     meta
    # TODO this needs a way to name this...
    def upload(self, obj, labels={}):
        # get timestamp *before* any other work
        timestamp = time_ns()

        # wrap bytes-like objects as file-like object for convinience
        if isinstance(obj, (bytes, bytearray)):
            obj = BytesIO(obj)

        tempdir = Path(self.root, '.tmp' + token_hex(8))
        tempdir.mkdir(parents=True, exist_ok=True)

        checksum = write_file_with_sha1sum(Path(tempdir, 'data'), obj)

        meta = {
            'timestamp': timestamp,
            'shasum': checksum,
            'labels': {k: v for k, v in labels.items()},
        }

        with Path(tempdir, 'meta').open('w') as f:
            json.dump(meta, f, separators=(',', ':'))

        # atomically move tempdir to real name
        filedir = Path(self.root, f'{timestamp}-{checksum}')
        tempdir.rename(filedir)
        return filedir
    
    def upload_file(self, path, keep=False, labels={}):
        path = Path(path)
        labels['filename'] = path.name
        with path.open('rb') as f:
            staged_path = self.upload(f, labels)
            if keep is False:
                path.unlink()
            return staged_path


def write_file_with_sha1sum(path, obj):
    h = hashlib.sha1()
    with path.open('wb') as f:
        while True:
            chunk = obj.read(32768)
            if len(chunk) == 0:
                break
            h.update(chunk)
            f.write(chunk)
    return h.hexdigest()


def parse_version_string(s: str) -> PluginVersion:
    m = re.match(r'(\d+)\.(\d+)\.(\d+)$', s)
    if m is None:
        raise ValueError(f'Invalid version string {s}.')
    return PluginVersion(
        major=int(m.group(1)),
        minor=int(m.group(2)),
        patch=int(m.group(3)))


# define global default instance of Plugin
plugin = Plugin(PluginConfig(
    name=os.environ.get('WAGGLE_PLUGIN_NAME', ''),
    id=int(os.environ.get('WAGGLE_PLUGIN_ID', 0)),
    version=parse_version_string(
        os.environ.get('WAGGLE_PLUGIN_VERSION', '0.0.0')),
    instance=int(os.environ.get('WAGGLE_PLUGIN_INSTANCE', 0)),
    username=os.environ.get('WAGGLE_PLUGIN_USERNAME', 'plugin'),
    password=os.environ.get('WAGGLE_PLUGIN_PASSWORD', 'plugin'),
    host=os.environ.get('WAGGLE_PLUGIN_HOST', 'rabbitmq'),
    port=int(os.environ.get('WAGGLE_PLUGIN_PORT', 5672)),
))
init = plugin.init
stop = plugin.stop
subscribe = plugin.subscribe
publish = plugin.publish
get = plugin.get

# define global default instance of Uploader
uploader = Uploader(Path(os.environ.get("WAGGLE_PLUGIN_UPLOAD_PATH", "/run/waggle/uploads")))
upload = uploader.upload
upload_file = uploader.upload_file
