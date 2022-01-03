import wagglemsg
import logging
from os import getenv
from threading import Event
from queue import Queue, Empty
import re
from typing import NamedTuple
from pathlib import Path
from contextlib import contextmanager
from .config import PluginConfig
from .rabbitmq import RabbitMQPublisher, RabbitMQConsumer
from .uploader import Uploader
from .time import get_timestamp, timeit_perf_counter, timeit_perf_counter_duration


logger = logging.getLogger(__name__)


class PublishData(NamedTuple):
    scope: str
    body: bytes


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
        self.stop.set()
        for task in self.tasks:
            task.done.wait()

    def subscribe(self, *topics):
        self.tasks.append(RabbitMQConsumer(topics, self.config, self.send, self.stop))

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
        msg = wagglemsg.Message(name=name, value=value, timestamp=timestamp, meta=meta)
        logger.debug("adding message to outgoing queue: %s", msg)
        self.send.put(PublishData(scope, wagglemsg.dump(msg)), timeout=timeout)

    def upload_file(self, path, meta={}, timestamp=None, keep=False):
        # get timestamp before doing other work
        timestamp = timestamp or get_timestamp()
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
            raise ValueError(f"publish name invalid: {s!r} part: {p!r}")
