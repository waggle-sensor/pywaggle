import numpy as np
from urllib.request import urlopen
from contextlib import contextmanager
from threading import Thread
from queue import Queue
import cv2
import time
import os


class ImageHandler:

    def __init__(self, url):
        self.url = url

    def close(self):
        pass

    def get(self):
        with urlopen(self.url) as f:
            data = f.read()
            ts = time.time_ns()
            arr = np.frombuffer(data, np.uint8)
            return ts, cv2.imdecode(arr, cv2.IMREAD_COLOR)


def video_worker(url, out):
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        raise RuntimeError(f'could not open camera at "{url}".')

    while True:
        ok, img = cap.read()
        if ok:
            # think about correct behavior for this
            # should expected the behavior be to make the latest
            out.put_nowait((time.time_ns(), img))
        else:
            time.sleep(0.01)


class VideoHandler:

    def __init__(self, url):
        self.queue = Queue()
        self.worker = Thread(target=video_worker, args=(
            url, self.queue), daemon=True)
        self.worker.start()

    def close(self):
        pass

    def get(self):
        return self.queue.get()


def get_camera_endpoint(name, **kwargs):
    return os.environ['WAGGLE_SES_CAMERA']


table = {
    'camera/image': (get_camera_endpoint, ImageHandler),
    'camera/video': (get_camera_endpoint, VideoHandler),
}


@contextmanager
def open_data_source(name, **kwargs):
    get_endpoint, handler = table[name]
    yield handler(get_endpoint(name, **kwargs))


if __name__ == '__main__':
    with open_data_source('camera/image', orientation='ground', min_resolution=(800, 600)) as dev:
        while True:
            ts, data = dev.get()
            print(ts, data)

# # select all temperature
# with waggle.open_data_source('env/temperature') as dev:
#     while True:
#         r = r.get()  # <- handle uses pika internally and queues up readings from exchange
#         print(r.timestamp, r.data)


# # select just from metsense board
# with waggle.open_data_source('sys/internal', sensor='htu21d') as r:
#     while True:
#         reading = r.get()
