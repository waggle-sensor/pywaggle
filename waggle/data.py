import numpy as np
from urllib.request import urlopen
from threading import Thread
from queue import Queue, Empty
import cv2
import time
import os
import socket
from pathlib import Path
import json
import random
import re
import pika


WAGGLE_DATA_CONFIG_PATH = Path(os.environ.get('WAGGLE_DATA_CONFIG_PATH', '/run/waggle/data-config.json'))

config = json.loads(WAGGLE_DATA_CONFIG_PATH.read_text())


class RandomHandler:

    def __init__(self, query, **kwargs):
        pass

    def get(self, timeout=None):
        return time.time(), random.random()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


class ImageHandler:

    def __init__(self, query, url):
        self.url = url

    def get(self, timeout=None):
        try:
            with urlopen(self.url, timeout=timeout) as f:
                data = f.read()
                ts = time.time()
                arr = np.frombuffer(data, np.uint8)
                return ts, cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except socket.timeout:
            raise TimeoutError('get timed out')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def video_worker(cap, out):
    while True:
        ok, img = cap.read()
        if ok:
            # think about correct behavior for this
            # should expected the behavior be to make the latest
            out.put_nowait((time.time(), img))
        else:
            time.sleep(0.01)

# TODO We need to use a flexible model where the data returned is
# extensible. For example, serial data won't really have a good
# notion of "timestamp". Maybe it's better to not include that.


class VideoHandler:

    def __init__(self, query, url):
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            raise RuntimeError(f'could not open camera at "{url}".')

        self.queue = Queue()

        worker = Thread(target=video_worker, args=(
            cap, self.queue), daemon=True)
        worker.start()

    def get(self, timeout=None):
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            raise TimeoutError('get timed out')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def pubsub_worker(topic, out):
    def callback(ch, method, properties, body):
        ts = properties.timestamp or time.time()
        out.put((ts, body))

    while True:
        try:
            connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(
                host='rabbitmq',
                credentials=pika.PlainCredentials('worker', 'worker')
            ))
            channel = connection.channel()

            result = channel.queue_declare(queue='', exclusive=True)
            queue = result.method.queue
            channel.queue_bind(exchange='data.topic', queue=queue, routing_key=topic)
            channel.basic_consume(
                queue=queue, on_message_callback=callback, auto_ack=True)

            channel.start_consuming()
        except Exception:
            time.sleep(1)


class PubSubHandler:

    def __init__(self, query):
        self.queue = Queue()
        worker = Thread(target=pubsub_worker, args=(
            query['type'], self.queue), daemon=True)
        worker.start()

    def get(self, timeout=None):
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            raise TimeoutError('get timed out')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def dict_is_subset(a, b):
    return all(k in b and re.match(b[k], a[k]) for k in a.keys())


def find_all_matches(query):
    return [c for c in config if dict_is_subset(query, c['match'])]


def find_match(query):
    matches = find_all_matches(query)
    if len(matches) == 0:
        raise RuntimeError('no matches found')
    if len(matches) > 1:
        raise RuntimeError('multiple devices found')
    return matches[0]


handlers = {
    'random': RandomHandler,
    'image': ImageHandler,
    'video': VideoHandler,
    'pubsub': PubSubHandler,
}

# optimizations *could* happen here, on demand...
def open_data_source(**query):
    match = find_match(query)
    handler = handlers[match['handler']['type']]
    args = match['handler']['args']
    return handler(query, **args)
