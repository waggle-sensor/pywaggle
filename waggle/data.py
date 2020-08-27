import numpy as np
from urllib.request import urlopen
from contextlib import contextmanager
from threading import Thread
from queue import Queue, Empty
import cv2
import time
import os
import socket
from pathlib import Path
import json
import random


with Path('data-config.json').open() as f:
    config = json.load(f)


class RandomHandler:

    def close(self):
        pass

    def get(self, timeout=None):
        return time.time_ns(), random.random()


class ImageHandler:

    def __init__(self, url):
        self.url = url

    def close(self):
        pass

    def get(self, timeout=None):
        try:
            with urlopen(self.url, timeout=timeout) as f:
                data = f.read()
                ts = time.time_ns()
                arr = np.frombuffer(data, np.uint8)
                return ts, cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except socket.timeout:
            raise TimeoutError('get timed out')


def video_worker(cap, out):
    while True:
        ok, img = cap.read()
        if ok:
            # think about correct behavior for this
            # should expected the behavior be to make the latest
            out.put_nowait((time.time_ns(), img))
        else:
            time.sleep(0.01)

# TODO We need to use a flexible model where the data returned is
# extensible. For example, serial data won't really have a good
# notion of "timestamp". Maybe it's better to not include that.


class VideoHandler:

    def __init__(self, url):
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            raise RuntimeError(f'could not open camera at "{url}".')

        self.queue = Queue()

        self.worker = Thread(target=video_worker, args=(
            cap, self.queue), daemon=True)
        self.worker.start()

    def close(self):
        pass

    def get(self, timeout=None):
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            raise TimeoutError('get timed out')


def dict_is_subset(a, b):
    return all(k in b and a[k] == b[k] for k in a.keys())


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
}


@contextmanager
def open_data_source(**kwargs):
    match = find_match(kwargs)
    handler = handlers[match['handler']['type']]
    yield handler(**match['handler']['args'])
