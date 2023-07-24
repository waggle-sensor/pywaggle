import cv2
from pathlib import Path
import numpy
from typing import Union
import os
from os import PathLike
import random
import json
import re
import threading
from queue import Queue
import time
from base64 import b64encode
from .timestamp import get_timestamp
from shutil import which
import ffmpeg
import logging

logger = logging.getLogger(__name__)


class BGR:
    @classmethod
    def cv2_to_format(cls, data):
        return data

    @classmethod
    def format_to_cv2(cls, data):
        return data


class RGB:
    @classmethod
    def cv2_to_format(cls, data):
        return cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

    @classmethod
    def format_to_cv2(cls, data):
        return cv2.cvtColor(data, cv2.COLOR_RGB2BGR)


WAGGLE_DATA_CONFIG_PATH = Path(
    os.environ.get("WAGGLE_DATA_CONFIG_PATH", "/run/waggle/data-config.json")
)


def read_device_config(path):
    config = json.loads(Path(path).read_text())
    return {
        section["match"]["id"]: section
        for section in config
        if "id" in section["match"]
    }


# TODO use format spec like rgb vs bgr in config file
class ImageSample:
    data: numpy.ndarray
    timestamp: int
    format: Union[BGR, RGB]

    def __init__(self, data, timestamp, format):
        self.format = format
        self.data = self.format.cv2_to_format(data)
        self.timestamp = timestamp

    def save(self, path: PathLike):
        path = Path(path)
        data = self.format.format_to_cv2(self.data)
        cv2.imwrite(str(path), data)

    def _repr_html_(self):
        data = self.format.format_to_cv2(self.data)
        ok, buf = cv2.imencode(".png", data)
        if not ok:
            raise RuntimeError("could not encode image")
        b64data = b64encode(buf.ravel()).decode()
        return f'<img src="data:image/png;base64,{b64data}" />'


class VideoSample:
    path: str
    timestamp: int

    def __init__(self, path, timestamp, format=RGB):
        self.format = format
        self.path = path
        self.timestamp = timestamp

    def __enter__(self):
        self.capture = cv2.VideoCapture(self.path)
        if not self.capture.isOpened():
            raise RuntimeError(
                f"unable to open video capture for file {self.path!r}"
            )
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        if self.fps > 100.:
            self.fps = 0.
            logger.debug(f'pywaggle cannot calculate timestamp because the fps ({self.fps}) is too high.')
        self.timestamp_delta = 1 / self.fps
        self._frame_count = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.capture.isOpened():
            self.capture.release()

    def __iter__(self):
        self._frame_count = 0
        return self

    def __next__(self):
        if self.capture == None or not self.capture.isOpened():
            raise RuntimeError("video is not opened. use the Python WITH statement to open the video")
        ok, data = self.capture.read()
        if not ok or data is None:
            raise StopIteration
        # timestamp must be an integer in nanoseconds
        approx_timestamp = int(self.timestamp + (self.timestamp_delta * self._frame_count))
        self._frame_count += 1
        return ImageSample(data=data, timestamp=approx_timestamp, format=self.format)


def resolve_device(device):
    if isinstance(device, Path):
        return resolve_device_from_path(device)
    # objects that are not paths or strings are considered already resolved
    if not isinstance(device, str):
        return device
    match = re.match(r"([A-Za-z0-9]+)://(.*)$", device)
    # non-url like paths refer to data shim devices
    if match is None:
        return resolve_device_from_data_config(device)
    # return file:// urls as path
    if match.group(1) == "file":
        return resolve_device_from_path(Path(match.group(2)))
    # return other urls as-is
    return device


def resolve_device_from_path(path):
    return str(path.absolute())


def resolve_device_from_data_config(device):
    config = read_device_config(WAGGLE_DATA_CONFIG_PATH)
    section = config.get(device)
    if section is None:
        raise KeyError(f"no device found {device!r}")
    try:
        return section["handler"]["args"]["url"]
    except KeyError:
        raise KeyError(f"missing .handler.args.url field for device {device!r}.")

class Camera:
    def __init__(self, device=0, format=RGB):
        self.capture = _Capture(resolve_device(device), format)

    def __enter__(self):
        self.capture.enable_daemon = True
        self.capture.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.capture.__exit__(exc_type, exc_val, exc_tb)

    def snapshot(self):
        with self.capture:
            return self.capture.snapshot()

    def stream(self):
        with self.capture:
            yield from self.capture.stream()

    def record(self, duration, file_path="./sample.mp4", skip_second=1):
        return self.capture.record(duration, file_path, skip_second)


class _Capture:
    def __init__(self, device, format):
        self.device = device
        self.format = format
        self.context_depth = 0
        self.enable_daemon = False
        self.daemon_need_to_stop = False
        self._ready_for_next_frame = Queue(maxsize=1)
        self.daemon = threading.Thread(target=self._run)
        self.lock = threading.Lock()

    def __enter__(self):
        if self.context_depth == 0:
            self.capture = cv2.VideoCapture(self.device)
            if not self.capture.isOpened():
                raise RuntimeError(
                    f"unable to open video capture for device {self.device!r}"
                )
            # spin up a thread to keep up with the camera frame rate
            if self.enable_daemon:
                self.daemon.start()
        self.context_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_depth -= 1
        if self.context_depth == 0:
            if self.enable_daemon:
                self.daemon_need_to_stop = True
                self.daemon.join()
            self.capture.release()
    
    def _run(self):
        # we sleep slighly shorter than FPS to drain the buffer efficiently
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        sleep = 0.01
        if fps > 0 and fps < 100:
            sleep = 1 / (fps + 1)
        logging.debug(f'camera FPS is {fps}. the background thread sleeps {sleep} seconds in between grab()')
        while not self.daemon_need_to_stop:
            self.lock.acquire()
            ok = self.capture.grab()
            if not ok:
                pass
                # TODO: what should we do when grab() fails?
                # raise RuntimeError("failed to grab a frame")
            self.timestamp = get_timestamp()
            self.lock.release()
            if self._ready_for_next_frame.empty():
                self._ready_for_next_frame.put_nowait(True)
            time.sleep(sleep)

    def grab_frame(self):
        if self.daemon.is_alive():
            self._ready_for_next_frame.get(block=True, timeout=60)
            self.lock.acquire()
            timestamp = self.timestamp
            ok, data = self.capture.retrieve()
            self.lock.release()
            if not ok:
                raise RuntimeError("failed to retrieve the taken snapshot")
            return ImageSample(data=data, timestamp=timestamp, format=self.format)
        else:
            ok = self.capture.grab()
            if not ok:
                raise RuntimeError("failed to take a snapshot")
            timestamp = get_timestamp()
            ok, data = self.capture.retrieve()
            if not ok:
                raise RuntimeError("failed to retrieve the taken snapshot")
            return ImageSample(data=data, timestamp=timestamp, format=self.format)

    def snapshot(self):
        return self.grab_frame()

    def stream(self):
        try:
            while True:
                yield self.grab_frame()
        except:
            pass

    def record(self, duration, file_path="./sample.mp4", skip_second=1):
        if which("ffmpeg") == None:
            raise RuntimeError("ffmpeg does not exist to record video. please install ffmpeg")
        if self.context_depth > 0:
            raise RuntimeError(f'the stream {self.device} is already open. please close first or use without the Python\'s WITH statement')
        if self.device.startswith("rtsp"):
            c = ffmpeg.input(self.device, rtsp_transport="tcp", ss=skip_second)
        else:
            c = ffmpeg.input(self.device, ss=skip_second)
        c = ffmpeg.output(c, file_path, codec="copy", f='mp4', t=duration).overwrite_output()
        timestamp = get_timestamp()
        _, stderr = ffmpeg.run(c, quiet=True)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return VideoSample(path=file_path, timestamp=timestamp)
        else:
            raise RuntimeError(f'error while recording: {stderr}')
        


class ImageFolder:
    available_formats = {".jpg", ".jpeg", ".png"}

    def __init__(self, root, format=RGB, shuffle=False):
        self.files = sorted(
            p.absolute()
            for p in Path(root).glob("*")
            if p.suffix in self.available_formats
        )
        self.format = format
        if shuffle:
            random.shuffle(self.files)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        data = cv2.imread(str(self.files[i]))
        timestamp = Path(self.files[i]).stat().st_mtime_ns
        return ImageSample(data=data, timestamp=timestamp, format=self.format)

    def __repr__(self):
        return f"ImageFolder{self.files!r}"
