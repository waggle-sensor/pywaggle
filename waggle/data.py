import numpy as np
from urllib.request import urlopen
from threading import Thread
from queue import Queue, Empty
import time
import os
import socket
from pathlib import Path
import json
import random
import re

try:
    import cv2
except ImportError:
    print('WARNING cv2 module not found. pywaggle requires this to capture image and video data.')


WAGGLE_DATA_CONFIG_PATH = Path(os.environ.get('WAGGLE_DATA_CONFIG_PATH', '/run/waggle/data-config.json'))

config = json.loads(WAGGLE_DATA_CONFIG_PATH.read_text())


# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy
try:
    from time import time_ns
except ImportError:
    def time_ns():
        return int(time.time() * 1e9)


class RandomHandler:

    def __init__(self, query, **kwargs):
        pass

    def get(self, timeout=None):
        return time_ns(), random.random()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def cvtColor(bgr_img, pixel_format='rgb'):
    if pixel_format == 'rgb':
        return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    return bgr_img


class ImageHandler:

    def __init__(self, query, url, pixel_format='rgb'):
        self.url = url
        self.pixel_format = pixel_format

    def get(self, timeout=None):
        try:
            with urlopen(self.url, timeout=timeout) as f:
                data = f.read()
                ts = time_ns()
                arr = np.frombuffer(data, np.uint8)
                bgr_img =  cv2.imdecode(arr, cv2.IMREAD_COLOR)
                return ts, cvtColor(bgr_img, self.pixel_format)
        except socket.timeout:
            raise TimeoutError('get timed out')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def video_worker(cap, out, pixel_format='rgb'):
    while True:
        ok, bgr_img = cap.read()
        if ok:
            img = cvtColor(bgr_img, pixel_format)
            # think about correct behavior for this
            # should expected the behavior be to make the latest
            out.put_nowait((time_ns(), img))
        else:
            time.sleep(0.01)

# TODO We need to use a flexible model where the data returned is
# extensible. For example, serial data won't really have a good
# notion of "timestamp". Maybe it's better to not include that.


class VideoHandler:

    def __init__(self, query, url, pixel_format='rgb'):
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            raise RuntimeError(f'could not open camera at "{url}".')

        self.queue = Queue()

        worker = Thread(target=video_worker, args=(
            cap, self.queue, pixel_format), daemon=True)
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
}

# optimizations *could* happen here, on demand...
def open_data_source(**query):
    match = find_match(query)
    handler = handlers[match['handler']['type']]
    args = match['handler']['args']
    return handler(query, **args)
