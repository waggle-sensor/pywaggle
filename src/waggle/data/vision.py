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
import time
from base64 import b64encode
from .timestamp import get_timestamp
from shutil import which
import ffmpeg
import logging
from contextlib import ExitStack, contextmanager


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
        self.capture = None

    def __enter__(self):
        self.capture = cv2.VideoCapture(self.path)
        if not self.capture.isOpened():
            raise RuntimeError(f"unable to open video capture for file {self.path!r}")
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        if self.fps > 100.0:
            self.fps = 0.0
            logger.debug(
                f"pywaggle cannot calculate timestamp because the fps ({self.fps}) is too high."
            )
            self.timestamp_delta = 0
        else:
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
            raise RuntimeError(
                "video is not opened. use the Python WITH statement to open the video"
            )
        ok, data = self.capture.read()
        if not ok or data is None:
            raise StopIteration
        # timestamp must be an integer in nanoseconds
        approx_timestamp = self.timestamp + int(
            self.timestamp_delta * self._frame_count * 1e9
        )
        self._frame_count += 1
        return ImageSample(data=data, timestamp=approx_timestamp, format=self.format)


INPUT_TYPE_FILE = "file"
INPUT_TYPE_OTHER = "other"


def resolve_device(device):
    if isinstance(device, Path):
        return resolve_device_from_path(device), INPUT_TYPE_FILE
    # objects that are not paths or strings are considered already resolved
    if not isinstance(device, str):
        return device, INPUT_TYPE_OTHER
    match = re.match(r"([A-Za-z0-9]+)://(.*)$", device)
    # non-url like paths refer to data shim devices
    if match is None:
        return resolve_device_from_data_config(device), INPUT_TYPE_OTHER
    # return file:// urls as path
    if match.group(1) == "file":
        return resolve_device_from_path(Path(match.group(2))), INPUT_TYPE_FILE
    # return other urls as-is
    return device, INPUT_TYPE_OTHER


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
        self.es = ExitStack()

        device, input_type = resolve_device(device)
        self.device = device
        self.format = format
        if input_type == "file":
            self.capture_class = FileCapture
        elif input_type == "other":
            self.capture_class = StreamCapture
        else:
            raise RuntimeError(f"invalid camera input type for device {device}")

    def __enter__(self):
        capture = self.capture_class(self.device, self.format)
        self.es.callback(capture.close)
        return capture

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.es.close()

    def snapshot(self):
        with self as capture:
            return capture.snapshot()

    def stream(self):
        with self as capture:
            yield from capture.stream()

    def record(self, duration, file_path="./sample.mp4", skip_second=1):
        if which("ffmpeg") is None:
            raise RuntimeError(
                "ffmpeg does not exist to record video. please install ffmpeg"
            )
        # TODO find cross platform option for webcams since likely to be used during tutorials
        if isinstance(self.device, int):
            c = ffmpeg.input(str(self.device), ss=skip_second)
        elif isinstance(self.device, str) and self.device.startswith("rtsp"):
            c = ffmpeg.input(self.device, rtsp_transport="tcp", ss=skip_second)
        else:
            c = ffmpeg.input(self.device, ss=skip_second)
        c = ffmpeg.output(
            c, file_path, codec="copy", f="mp4", t=duration
        ).overwrite_output()
        timestamp = get_timestamp()

        try:
            ffmpeg.run(c, quiet=True)
        except ffmpeg.Error as e:
            raise RuntimeError(f"error while recording: {e.stderr.decode()}")

        return VideoSample(path=file_path, timestamp=timestamp)


class FileCapture:
    def __init__(self, device, format):
        self.device = device
        self.format = format

    def close(self):
        print("bye file!")

    def snapshot(self):
        pass

    def stream(self):
        pass

    def record(self):
        raise RuntimeError("TODO write this error")


class StreamCapture:
    def __init__(self, device, format):
        self.device = device
        self.format = format

        self.capture = cv2.VideoCapture(self.device)
        if not self.capture.isOpened():
            raise RuntimeError(
                f"unable to open video capture for device {self.device!r}"
            )

        self.lock = threading.Lock()
        self.daemon_need_to_stop = threading.Event()
        self._ready_for_next_frame = threading.Event()
        self.stopped = threading.Event()
        threading.Thread(target=self._run, daemon=True).start()

    def close(self):
        self.daemon_need_to_stop.set()
        self.stopped.wait(timeout=10)
        self.capture.release()

    def snapshot(self):
        return self.grab_frame()

    def stream(self):
        while True:
            yield self.grab_frame()

    def record(self):
        raise RuntimeError("TODO write this error")

    def _run(self):
        # we sleep slighly shorter than FPS to drain the buffer efficiently
        # NOTE: OpenCV's FPS get function is inaccurate as a USB webcam gives 1 FPS while
        #       a RTSP stream returns 180000. none of them are correct. therefore, we cannot
        #       decide the sleep time based on obtained FPS
        # fps = self.capture.get(cv2.CAP_PROP_FPS)
        sleep = 0.01
        # if fps > 0 and fps < 100:
        #    sleep = 1 / (fps + 1)
        # logging.debug(f'camera FPS is {fps}. the background thread sleeps {sleep} seconds in between grab()')
        try:
            while not self.daemon_need_to_stop.is_set():
                with acquire_with_timeout(self.lock, timeout=10.0):
                    ok = self.capture.grab()
                    if not ok:
                        raise RuntimeError("failed to grab a frame")
                    self.timestamp = get_timestamp()
                self._ready_for_next_frame.set()
                time.sleep(sleep)
        finally:
            self.stopped.set()

    def grab_frame(self):
        if not self._ready_for_next_frame.wait(timeout=10.0):
            raise RuntimeError(
                "failed to grab a frame from the background thread: timed out"
            )
        self._ready_for_next_frame.clear()
        with acquire_with_timeout(self.lock, timeout=1.0):
            timestamp = self.timestamp
            ok, data = self.capture.retrieve()
            if not ok:
                raise RuntimeError("failed to retrieve the taken snapshot")
        return ImageSample(data=data, timestamp=timestamp, format=self.format)


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


@contextmanager
def acquire_with_timeout(lock, timeout):
    try:
        lock.acquire(timeout=timeout)
        yield
    finally:
        lock.release()
