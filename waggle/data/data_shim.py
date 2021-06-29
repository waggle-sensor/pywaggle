import logging
import numpy as np
from urllib.request import urlopen
from threading import Thread, Event
from queue import Queue, Empty, Full
import time
import os
import socket
from pathlib import Path
import json
import random
import re

logger = logging.getLogger(__name__)

try:
    import cv2
except ImportError:
    logger.warning('cv2 module not found. pywaggle requires this to capture image and video data.')


# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy
try:
    from time import time_ns
except ImportError:
    logger.warning('using backwards compatible implementation of time_ns')
    def time_ns():
        return int(time.time() * 1e9)


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


def video_worker(handler):
    try:
        while not handler.quit.is_set():
            ok, bgr_img = handler.cap.read()
            if not ok:
                break
            img = cvtColor(bgr_img, handler.pixel_format)
            item = (time_ns(), img)
            
            # attempt to add an item to the queue
            try:
                handler.queue.put_nowait(item)
                continue
            except Full:
                logger.debug("video frame queue full. evicting oldest frame...")
            # evict an item from queue
            try:
                handler.queue.get_nowait()
            except Empty:
                pass
            # queue should have space to add now. (assuming this
            # is the only producer adding to this queue)
            handler.queue.put_nowait(item)
    finally:
        handler.cap.release()
        handler.released.set()


# TODO We need to use a flexible model where the data returned is
# extensible. For example, serial data won't really have a good
# notion of "timestamp". Maybe it's better to not include that.


class VideoHandler:

    def __init__(self, query, url, pixel_format='rgb'):
        self.pixel_format = pixel_format
        self.cap = cv2.VideoCapture(url)
        if not self.cap.isOpened():
            raise RuntimeError(f'could not open camera at "{url}".')
        self.queue = Queue(8)
        self.quit = Event()
        self.released = Event()
        # NOTE(sean) no further mutation can be done on VideoHandler state. all
        # interaction with cap *must* be done in the worker thread or via queue
        # and quit primitives
        worker = Thread(target=video_worker, args=(self,), daemon=True)
        worker.start()

    def get(self, timeout=None):
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            raise TimeoutError('get timed out')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.quit.set()
        self.released.wait() # <- wait for cleanup in worker thread


WAGGLE_DATA_CONFIG_PATH = Path(os.environ.get('WAGGLE_DATA_CONFIG_PATH', '/run/waggle/data-config.json'))

try:
    config = json.loads(WAGGLE_DATA_CONFIG_PATH.read_text())
except FileNotFoundError:
    logger.debug('could not find data config file %s. using empty resource list.', WAGGLE_DATA_CONFIG_PATH)
    config = []


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
    'image': ImageHandler,
    'video': VideoHandler,
}

# optimizations *could* happen here, on demand...
def open_data_source(**query):
    match = find_match(query)
    handler = handlers[match['handler']['type']]
    args = match['handler']['args']
    return handler(query, **args)
