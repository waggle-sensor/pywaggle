import logging
import re
import wagglemsg

from contextlib import contextmanager
from datetime import datetime
from os import getenv
from pathlib import Path
from queue import Queue, Empty
from threading import Event
from typing import NamedTuple

from .config import PluginConfig
from .rabbitmq import RabbitMQPublisher, RabbitMQConsumer
from .time import get_timestamp, timeit_perf_counter, timeit_perf_counter_duration
from .uploader import Uploader


logger = logging.getLogger(__name__)


class PublishData(NamedTuple):
    scope: str
    body: bytes


# Nanoseconds since epoch for 2000-01-01T00:00:00Z
MIN_TIMESTAMP_NS = 946706400000000000


class FilesystemPublisher:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.datafile = Path(root, "data.ndjson").open("a")
        self.uploads_dir = Path(root, "uploads")
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def close(self):
        self.datafile.close()

    def publish(self, msg: wagglemsg.Message):
        import json

        out = {
            "name": msg.name,
            "value": msg.value,
            "meta": msg.meta,
            # python doesn't have builtin support for nanosecond
            "timestamp": isoformat_time_ns(msg.timestamp),
        }
        print(
            json.dumps(out, sort_keys=True, separators=(",", ":")),
            file=self.datafile,
            flush=True,
        )

    def upload_file(self, path, timestamp, meta):
        from shutil import copyfile

        src = Path(path)
        dst = Path(self.uploads_dir, f"{timestamp}-{src.name}")
        copyfile(src, dst)
        meta = meta.copy()
        meta["filename"] = Path(src).name
        self.publish(
            wagglemsg.Message(
                name="upload",
                value=str(dst.absolute()),
                meta=meta,
                timestamp=timestamp,
            )
        )


def isoformat_time_ns(ns: int) -> str:
    # python doesn't have builtin support for nanosecond timestamps and formatting, so we provide
    # a backfill for it. this is only intended to be used in the run log for testing.
    nanostr = f"{ns%1000:03d}"
    return datetime.fromtimestamp(ns / 1e9).isoformat() + nanostr


class Plugin:
    """
    Plugin provides methods to publish and consume messages inside the Waggle ecosystem.

    Examples
    --------

    The simplest example is creating a Plugin and publishing a message. This can be done using:

    ```python
    from waggle.plugin import Plugin

    with Plugin() as plugin:
        plugin.publish("test_value", 99)
    ```
    """

    def __init__(
        self, config=None, uploader=None, file_publisher: FilesystemPublisher = None
    ):
        self.config = config or get_default_plugin_config()
        self.uploader = uploader or get_default_plugin_uploader()
        self.send = Queue()
        self.recv = Queue()
        self.stop = Event()
        self.tasks = []

        # TODO(sean) can we use ExitStack to clean up???

        self.file_publisher = file_publisher

        if self.file_publisher is None and getenv("PYWAGGLE_LOG_DIR") is not None:
            self.file_publisher = FilesystemPublisher(getenv("PYWAGGLE_LOG_DIR"))

    def __enter__(self):
        self.tasks.append(RabbitMQPublisher(self.config, self.send, self.stop))
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop.set()

        if self.file_publisher is not None:
            self.file_publisher.close()

        for task in self.tasks:
            task.done.wait()

    def subscribe(self, *topics):
        self.tasks.append(RabbitMQConsumer(topics, self.config, self.recv, self.stop))
        # TODO(sean) add mock or integration testing against rabbitmq to actually test this

    def get(self, timeout=None):
        try:
            return self.recv.get(timeout=timeout)
        except Empty:
            pass
        raise TimeoutError("plugin get timed out")

    def publish(self, name, value, meta={}, timestamp=None, scope="all", timeout=None):
        # get timestamp before doing other work
        timestamp = timestamp or get_timestamp()
        raise_for_invalid_publish_name(name)
        self.__publish(name, value, meta, timestamp, scope, timeout)

    # NOTE __publish is used internally by publish and upload_file to do an unchecked
    # message publish. the main reason this exists is to guard against reserved names
    # like "upload" in publish but still allow upload_file to use it.
    def __publish(self, name, value, meta, timestamp, scope="all", timeout=None):
        if not isinstance(value, (int, float, str)):
            raise TypeError("Value must be an int, float or str.")
        if not isinstance(timestamp, int):
            raise TypeError(
                "Timestamp must be an int and have units of nanoseconds since epoch. Please see the documentation for more information on setting timestamps."
            )
        if timestamp < MIN_TIMESTAMP_NS:
            raise ValueError(
                "Timestamp probably has wrong units and is being processed as before 2000-01-01T00:00:00Z. Timestamp must have units of nanoseconds since epoch. Please see the documentation for more information on setting timestamps."
            )
        if not valid_meta(meta):
            raise TypeError("Meta must be a dictionary of strings to strings.")
        msg = wagglemsg.Message(name=name, value=value, timestamp=timestamp, meta=meta)

        # hack to use file publisher for everything except uploads
        if self.file_publisher is not None and name != "upload":
            self.file_publisher.publish(msg)

        logger.debug("adding message to outgoing queue: %s", msg)
        self.send.put(PublishData(scope, wagglemsg.dump(msg)), timeout=timeout)

    def upload_file(self, path, meta={}, timestamp=None, keep=False):
        # get timestamp before doing other work
        timestamp = timestamp or get_timestamp()

        if self.file_publisher is not None:
            self.file_publisher.upload_file(path, meta=meta, timestamp=timestamp)

        if self.uploader is not None:
            meta = meta.copy()
            meta["filename"] = Path(path).name
            upload_path = self.uploader.upload_file(
                path=path, meta=meta, timestamp=timestamp, keep=keep
            )
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


def get_default_plugin_config() -> PluginConfig:
    return PluginConfig(
        username=getenv("WAGGLE_PLUGIN_USERNAME", "plugin"),
        password=getenv("WAGGLE_PLUGIN_PASSWORD", "plugin"),
        host=getenv("WAGGLE_PLUGIN_HOST", "rabbitmq"),
        port=int(getenv("WAGGLE_PLUGIN_PORT", 5672)),
        app_id=getenv("WAGGLE_APP_ID", ""),
    )


def valid_meta(meta):
    return isinstance(meta, dict) and all(isinstance(v, str) for v in meta.values())


def get_default_plugin_uploader():
    if (
        getenv("WAGGLE_PLUGIN_UPLOAD_PATH") is None
        and getenv("PYWAGGLE_LOG_DIR") is not None
    ):
        return None
    return Uploader(Path(getenv("WAGGLE_PLUGIN_UPLOAD_PATH", "/run/waggle/uploads")))


publish_name_part_pattern = re.compile("^[a-z0-9_]+$")


def raise_for_invalid_publish_name(s: str):
    if not isinstance(s, str):
        raise TypeError(f"publish name must be a string: {s!r}")
    if len(s) > 128:
        raise ValueError(f"publish must be at most 128 characters: {s!r}")
    if s == "upload":
        raise ValueError(f"name {s!r} is reserved for system use only")
    parts = s.split(".")
    for p in parts:
        if not publish_name_part_pattern.match(p):
            raise ValueError(
                f"publish name invalid: {s!r} part: {p!r} (names must consist of [a-z0-9_] and may be joined by .)"
            )
