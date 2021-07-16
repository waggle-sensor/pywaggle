import cv2
from pathlib import Path
import numpy
from typing import Union
from contextlib import contextmanager
import time
import os
import random
import json
import re
from .timestamp import get_timestamp


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


# class HSV:

#     @classmethod
#     def cv2_to_format(cls, data):
#         return cv2.cvtColor(data, cv2.COLOR_BGR2HSV)

#     @classmethod
#     def format_to_cv2(cls, data):
#         return cv2.cvtColor(data, cv2.COLOR_HSV2BGR)


WAGGLE_DATA_CONFIG_PATH = Path(os.environ.get('WAGGLE_DATA_CONFIG_PATH', '/run/waggle/data-config.json'))


def read_device_config(path):
    config = json.loads(Path(path).read_text())
    return {section["match"]["id"]: section for section in config if "id" in section["match"]}


# TODO use format spec like rgb vs bgr in config file
class ImageSample:
    data: numpy.ndarray
    timestamp: int
    format: Union[BGR, RGB]

    def __init__(self, data, timestamp, format):
        self.format = format
        self.data = self.format.cv2_to_format(data)
        self.timestamp = timestamp

    def save(self, filename):
        cv2.imwrite(filename, self.format.format_to_cv2(self.data))


# TODO(sean) handle various data sources more uniformly
def resolve_device(device):
    # path like files are converted to strings for opencv
    if isinstance(device, Path):
        return str(device.absolute())
    # objects that are not paths or strings are considered already resolved
    if not isinstance(device, str):
        return device
    # url like strings are considered resolved
    if re.match(r"[A-Za-z0-9]+://", device):
        return device
    # otherwise, lookup device in data config
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
        self.device = resolve_device(device)
        self.format = format

    def snapshot(self, dropframes=0):

        with VideoCapture(self.device) as capture:
            # drop first few frames to improve exposure
            for _ in range(dropframes):
                capture.read()
            timestamp = get_timestamp()
            ok, data = capture.read()
            if not ok:
                raise RuntimeError("failed to take snapshot")
            return ImageSample(data=data, timestamp=timestamp, format=self.format)

    def stream(self):
        with VideoCapture(self.device) as capture:
            while True:
                timestamp = get_timestamp()
                ok, data = capture.read()
                if not ok:
                    break
                yield ImageSample(data=data, timestamp=timestamp, format=self.format)


@contextmanager
def VideoCapture(device):
    capture = cv2.VideoCapture(device)
    if not capture.isOpened():
        raise RuntimeError(f"unable to open video capture for device {device!r}")
    try:
        yield capture
    finally:
        capture.release()


class ImageFolder:

    available_formats = {".jpg", ".jpeg", ".png"}

    def __init__(self, root, format=RGB, shuffle=False):
        self.files = sorted(p.absolute() for p in Path(root).glob("*") if p.suffix in self.available_formats)
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
