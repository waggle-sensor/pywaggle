import cv2
from pathlib import Path
import numpy
from typing import Union
import os
from os import PathLike
import random
import json
import re
from base64 import b64encode
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


class _Capture:

    def __init__(self, device, format):
        self.device = device
        self.format = format
        self.context_depth = 0

    def __enter__(self):
        if self.context_depth == 0:
            self.capture = cv2.VideoCapture(self.device)
            if not self.capture.isOpened():
                raise RuntimeError(f"unable to open video capture for device {self.device!r}")
        self.context_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_depth -= 1
        if self.context_depth == 0:
            self.capture.release()

    def snapshot(self):
        timestamp = get_timestamp()
        ok, data = self.capture.read()
        if not ok:
            raise RuntimeError("failed to take snapshot")
        return ImageSample(data=data, timestamp=timestamp, format=self.format)

    def stream(self):
        while True:
            timestamp = get_timestamp()
            ok, data = self.capture.read()
            if not ok:
                break
            yield ImageSample(data=data, timestamp=timestamp, format=self.format)


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
