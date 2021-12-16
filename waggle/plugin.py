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
from contextlib import contextmanager
from copy import deepcopy


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

# NOTE to preserve the best accuracy, we implement the backwards compatible perf
# counter by only abstracting how to measure the duration between two times in
# nanoseconds
try:
    from time import perf_counter_ns as timeit_perf_counter

    def timeit_perf_counter_duration(start, finish):
        return finish - start
except ImportError:
    from time import perf_counter as timeit_perf_counter

    def timeit_perf_counter_duration(start, finish):
        return int((finish - start) * 1e9)


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


def get_default_plugin_config() -> PluginConfig:
    return PluginConfig(
        username=getenv("WAGGLE_PLUGIN_USERNAME", "plugin"),
        password=getenv("WAGGLE_PLUGIN_PASSWORD", "plugin"),
        host=getenv("WAGGLE_PLUGIN_HOST", "rabbitmq"),
        port=int(getenv("WAGGLE_PLUGIN_PORT", 5672)),
        app_id=getenv("WAGGLE_APP_ID", ""),
    )


def get_default_plugin_uploader():
    return Uploader(Path(getenv("WAGGLE_PLUGIN_UPLOAD_PATH", "/run/waggle/uploads")))


class Plugin:

    def __init__(self, config=None, uploader=None):
        self.config = config or get_default_plugin_config()
        self.uploader = uploader or get_default_plugin_uploader()
        self.send = Queue()
        self.recv = Queue()
        self.stop = Event()
        self.tasks = []

    def __enter__(self):
        self.tasks.append(RabbitMQPublisher(self.config, self.send, self.stop))
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # signal to tasks to stop
        self.stop.set()
        # wait for all tasks to finish
        for task in self.tasks:
            task.done.wait()

    def get(self, timeout=None):
        try:
            return self.incoming_queue.get(timeout=timeout)
        except Empty:
            pass
        raise TimeoutError("plugin get timed out")

    def subscribe(self, *topics):
        self.tasks.append(RabbitMQConsumer(topics, self.config, self.send, self.stop))

    def publish(self, name, value, meta={}, timestamp=None, scope="all", timeout=None):
        if timestamp is None:
            timestamp = get_timestamp()
        raise_for_invalid_publish_name(name)
        self.__publish(name, value, meta, timestamp, scope, timeout)

    # NOTE __publish is used internally by publish and upload_file to do an unchecked
    # message publish. the main reason this exists is to guard against reserved names
    # like "upload" in publish but still allow upload_file to use it.
    def __publish(self, name, value, meta, timestamp, scope="all", timeout=None):
        msg = wagglemsg.Message(name=name, value=value, timestamp=timestamp, meta=meta)
        logger.debug("adding message to outgoing queue: %s", msg)
        self.send.put((scope, wagglemsg.dump(msg)), timeout=timeout)

    def upload_file(self, path, meta={}, timestamp=None, keep=False):
        if timestamp is None:
            timestamp = get_timestamp()
        upload_path = self.uploader.upload_file(path=path, meta=meta, timestamp=timestamp, keep=keep)
        # copy metadata and set filename
        # TODO consolidate this with Uploader...
        meta = meta.copy()
        meta["filename"] = Path(path).name
        self.__publish("upload", upload_path.name, meta, timestamp)

    @contextmanager
    def timeit(self, name):
        logger.debug("starting timeit block %s", name)
        start = timeit_perf_counter()
        yield
        finish = timeit_perf_counter()
        duration = timeit_perf_counter_duration(start, finish)
        self.publish(name, duration)
        logger.debug("finished timeit block %s", name)


def get_connection_parameters_for_config(config: PluginConfig) -> pika.ConnectionParameters:
    return pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=pika.PlainCredentials(
                username=config.username,
                password=config.password,
            ),
            connection_attempts=1,
            socket_timeout=1.0,
        )


class RabbitMQPublisher:
    """
    RabbitMQPublisher manages a connection to a RabbitMQ broker and flushes messages from
    the provided queue when connected.

    This is done using a background which must be stopped by setting the provided stop Event.
    """

    def __init__(self, config: PluginConfig, messages: Queue, stop: Event):
        self.config = deepcopy(config)
        self.params = get_connection_parameters_for_config(config)
        self.messages = messages
        self.stop = stop
        self.done = Event()
        Thread(target=self.__main).start()
    
    def __main(self):
        try:
            while not self.stop.is_set():
                try:
                    self.__connect_and_flush_messages()
                except Exception:
                    time.sleep(1)
        finally:
            self.done.set()

    def __connect_and_flush_messages(self):
        with pika.BlockingConnection(self.params) as conn, conn.channel() as ch:
            while not self.stop.is_set():
                self.__flush_messages(ch)
            # attempt to flush any remaining messages
            self.__flush_messages(ch)

    def __flush_messages(self, ch):
        while True:
            try:
                scope, body = self.messages.get(timeout=1)
            except Empty:
                return

            properties = pika.BasicProperties(
                delivery_mode=2,
                user_id=self.params.credentials.username)
            
            # NOTE app_id is used by data service to validate and tag additional metadata provided by k3s scheduler.
            if self.config.app_id != "":
                properties.app_id = self.config.app_id

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("publishing message to rabbitmq: %s", wagglemsg.load(body))

            ch.basic_publish(
                exchange="to-validator",
                routing_key=scope,
                properties=properties,
                body=body)


class RabbitMQConsumer:
    """
    RabbitMQConsumer manages a connection to a RabbitMQ broker and adds incoming messages to
    the provided queue when connected.

    This is done using a background which must be stopped by setting the provided stop Event.
    """

    def __init__(self, topics, config: PluginConfig, messages: Queue, stop: Event):
        self.topics = deepcopy(topics)
        self.config = deepcopy(config)
        self.params = get_connection_parameters_for_config(config)
        self.messages = messages
        self.stop = stop
        self.done = Event()
        Thread(target=self.__main).start()

    def __main(self):
        try:
            while not self.stop.is_set():
                try:
                    self.__connect_and_consume_messages()
                except Exception:
                    time.sleep(1)
        finally:
            self.done.set()

    def __connect_and_consume_messages(self):
        with pika.BlockingConnection(self.params) as conn, conn.channel() as ch:
            # setup subscriber queue and bind to topics
            queue = ch.queue_declare("", exclusive=True).method.queue
            ch.basic_consume(queue, self.__process_message, auto_ack=True)
            ch.queue_bind(queue, "data.topic", self.topics)

            def check_stop():
                if self.stop.is_set():
                    ch.stop_consuming()
                else:
                    conn.call_later(1, check_stop)

            conn.call_later(1, check_stop)
            ch.start_consuming()
    
    def __process_message(self, ch, method, properties, body):
        try:
            msg = wagglemsg.load(body)
        except TypeError:
            logger.debug("unsupported message type: %s %s", properties, body)
            return
        self.messages.put(msg)


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


# NOTE inform users of change until we migrate everyone
def init():
    raise DeprecationWarning("Calling init explicity is deprecated. Please use the context manager format \"with Plugin() as plugin\" instead.")
