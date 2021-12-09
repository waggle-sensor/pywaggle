#!/usr/bin/env python3
# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import wagglemsg
import json
import logging
from os import getenv
import pika
import pika.exceptions
from threading import Thread, Event
from queue import Queue, Empty
import time
import re
from typing import NamedTuple
from pathlib import Path
import hashlib
from shutil import copyfile


logger = logging.getLogger(__name__)
# turn down pika's logger automatically. by default, it's very verbose.
logging.getLogger("pika").setLevel(logging.CRITICAL)


# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy 
try:
    from time import time_ns as get_timestamp
except ImportError:
    def get_timestamp():
        return int(time.time() * 1e9)


class PluginConfig(NamedTuple):
    username: str
    password: str
    host: str
    port: int
    app_id: str


publish_name_part_pattern = re.compile("^[a-z0-9_]+$")

def raise_for_invalid_publish_name(s):
    if not isinstance(s, str):
        raise TypeError(f"publish name must be a string: {s!r}")
    if len(s) > 128:
        raise ValueError(f"publish must be at most 128 characters: {s!r}")
    if s == "upload":
        raise ValueError(f"name {s!r} is reserved for system use only")
    parts = s.split(".")
    for p in parts:
        if not publish_name_part_pattern.match(p):
            raise ValueError(f"publish name invalid: {s!r} part: {p!r}")


class Plugin:

    def __init__(self, config=None, uploader=None):
        # default config from env vars
        if config is None:
            config = PluginConfig(
                username=getenv("WAGGLE_PLUGIN_USERNAME", "plugin"),
                password=getenv("WAGGLE_PLUGIN_PASSWORD", "plugin"),
                host=getenv("WAGGLE_PLUGIN_HOST", "rabbitmq"),
                port=int(getenv("WAGGLE_PLUGIN_PORT", 5672)),
                app_id=getenv("WAGGLE_APP_ID", ""),
            )

        self.config = config

        # default upload directory
        if uploader is None:
            uploader = Uploader(Path(getenv("WAGGLE_PLUGIN_UPLOAD_PATH", "/run/waggle/uploads")))

        self.uploader = uploader

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

        self.outgoing_queue = Queue()
        self.incoming_queue = Queue()
        self.subscribe_queue = Queue()

    def __enter__(self):
        self.init()
        # self.publish("plugin.status", "start")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # if exc_type is None:
        #     self.publish("plugin.status", "stop")
        # else:
        #     self.publish("plugin.status", "error")
        self.stop()

    def init(self):
        logger.debug("starting plugin worker thread")
        if self.running.is_set():
            raise RuntimeError("cannot init already running plugin")
        self.running.set()
        Thread(target=self.run_rabbitmq_worker, daemon=True).start()

    def stop(self, timeout=None):
        logger.debug("stopping plugin worker thread")
        self.running.clear()
        self.stopped.wait(timeout=timeout)

    def get(self, timeout=None):
        try:
            return self.incoming_queue.get(timeout=timeout)
        except Empty:
            pass
        raise TimeoutError("plugin get timed out")

    def subscribe(self, *topics):
        self.subscribe_queue.put(topics)
    
    # NOTE __publish is used internally by publish and upload_file to do an unchecked
    # message publish. the main reason this exists is to guard against reserved names
    # like "upload" in publish but still allow upload_file to use it.
    def __publish(self, name, value, meta, timestamp, scope="all", timeout=None):
        msg = wagglemsg.Message(name=name, value=value, timestamp=timestamp, meta=meta)
        logger.debug("adding message to outgoing queue: %s", msg)
        self.outgoing_queue.put((scope, wagglemsg.dump(msg)), timeout=timeout)
    
    def publish(self, name, value, meta={}, timestamp=None, scope="all", timeout=None):
        if timestamp is None:
            timestamp = get_timestamp()
        raise_for_invalid_publish_name(name)
        self.__publish(name, value, meta, timestamp, scope, timeout)

    def upload_file(self, path, meta={}, timestamp=None, keep=False):
        if timestamp is None:
            timestamp = get_timestamp()
        upload_path = self.uploader.upload_file(path=path, meta=meta, timestamp=timestamp, keep=keep)
        # copy metadata and set filename
        # TODO consolidate this with Uploader...
        meta = meta.copy()
        meta["filename"] = Path(path).name
        self.__publish("upload", upload_path.name, meta, timestamp)

    def run_rabbitmq_worker(self):
        try:
            self.stopped.clear()
            while self.running.is_set():
                try:
                    logger.debug("connecting to rabbitmq broker at %s:%d with username %r",
                                    self.connection_parameters.host,
                                    self.connection_parameters.port,
                                    self.connection_parameters.credentials.username)
                    with pika.BlockingConnection(self.connection_parameters) as connection:
                        logger.debug("connected to rabbitmq broker")
                        self.rabbitmq_worker_mainloop(connection)
                except Exception as exc:
                    logger.debug("rabbitmq connection error: %s", exc)
                time.sleep(1)
        finally:
            self.stopped.set()

    def rabbitmq_worker_mainloop(self, connection):
        channel = connection.channel()

        def subscriber_callback(ch, method, properties, body):
            try:
                msg = wagglemsg.load(body)
            except TypeError:
                logger.debug("unsupported message type: %s %s", properties, body)
                return
            self.incoming_queue.put(msg)
        
        def process_subscribe_queue():
            while self.running.is_set():
                try:
                    topics = self.subscribe_queue.get_nowait()
                except Empty:
                    break
                for topic in topics:
                    logger.debug("subscribing to topic %r", topic)
                    channel.queue_bind(queue, "data.topic", topic)

        def process_publish_queue():
            while self.running.is_set():
                try:
                    scope, body = self.outgoing_queue.get_nowait()
                except Empty:
                    break
                properties = pika.BasicProperties(
                    delivery_mode=2,
                    user_id=self.connection_parameters.credentials.username)
                
                if self.config.app_id != "":
                    properties.app_id = self.config.app_id
                    # NOTE app_id is used by data service to validate and tag additional metadata provided by k3s scheduler.

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("publishing message to rabbitmq: %s", wagglemsg.load(body))

                channel.basic_publish(
                    exchange="to-validator",
                    routing_key=scope,
                    properties=properties,
                    body=body)

        def process_queues_and_events():
            process_subscribe_queue()
            process_publish_queue()
            if self.running.is_set():
                connection.call_later(0.01, process_queues_and_events)
            else:
                logger.debug("stopping rabbitmq processing loop")
                channel.stop_consuming()

        # setup subscriber queue and bind
        queue = channel.queue_declare("", exclusive=True).method.queue
        channel.basic_consume(queue, subscriber_callback, auto_ack=True)
        # setup periodic publish and subscribe to topic checks
        connection.call_later(0.01, process_queues_and_events)
        logger.debug("starting rabbitmq processing loop")
        channel.start_consuming()


class Uploader:

    def __init__(self, root):
        self.root = Path(root)

    # NOTE uploads are stored in the following directory structure:
    # root/
    #   timestamp-sha1sum/
    #     data
    #     meta
    def upload_file(self, path, meta={}, timestamp=None, keep=False):
        # get timestamp *before* doing any other work!
        if timestamp is None:
            timestamp = get_timestamp()

        path = Path(path)

        checksum = sha1sum_for_file(path)

        # create upload dir
        upload_dir = Path(self.root, f"{timestamp}-{checksum}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # stage data file
        # NOTE we do a copy instead of move, as the upload dir may
        # be mounted from another disk.
        copyfile(path, Path(upload_dir, "data"))
        if not keep:
            path.unlink()

        # stage meta file
        metafile = {
            "timestamp": timestamp,
            "shasum": checksum,
            "labels": {k: v for k, v in meta.items()},
        }
        metafile["labels"]["filename"] = path.name
        write_json_file(Path(upload_dir, "meta"), metafile)

        return upload_dir


def sha1sum_for_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(32768)
            if chunk == b"":
                break
            h.update(chunk)
    return h.hexdigest()


def write_json_file(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, separators=(',', ':'), sort_keys=True)


# define global default instance of Plugin
plugin = Plugin()
init = plugin.init
stop = plugin.stop
subscribe = plugin.subscribe
publish = plugin.publish
get = plugin.get
upload_file = plugin.upload_file
