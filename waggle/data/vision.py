import cv2
from pathlib import Path
import numpy
from typing import NamedTuple
from contextlib import contextmanager
import time
import os
import random
import json
import re
from .timestamp import get_timestamp


WAGGLE_DATA_CONFIG_PATH = Path(os.environ.get('WAGGLE_DATA_CONFIG_PATH', '/run/waggle/data-config.json'))


def read_device_config(path):
    config = json.loads(Path(path).read_text())
    return {section["match"]["id"]: section for section in config if "id" in section["match"]}


# TODO use format spec like rgb vs bgr in config file
class ImageSample(NamedTuple):
    data: numpy.ndarray
    timestamp: int

    def save(self, filename):
        # NOTE cv2 assumes BGR images, so to save our image we convert back to the orignal format
        cv2.imwrite(filename, cv2.cvtColor(self.data, cv2.COLOR_RGB2BGR))


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

def bgr2rgb(data):
    return cv2.cvtColor(data, cv2.COLOR_BGR2RGB)


class Camera:

    def __init__(self, device=0):
        self.device = resolve_device(device)

    def snapshot(self, dropframes=0):

        with VideoCapture(self.device) as capture:
            # drop first few frames to improve exposure
            for _ in range(dropframes):
                capture.read()
            timestamp = get_timestamp()
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("failed to take snapshot")
            return ImageSample(data=bgr2rgb(frame), timestamp=timestamp)

    def stream(self):
        with VideoCapture(self.device) as capture:
            while True:
                timestamp = get_timestamp()
                ok, frame = capture.read()
                if not ok:
                    break
                yield ImageSample(data=bgr2rgb(frame), timestamp=timestamp)


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

    def __init__(self, root, shuffle=False):
        self.files = sorted(p.absolute() for p in Path(root).glob("*") if p.suffix in self.available_formats)
        if shuffle:
            random.shuffle(self.files)

    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, i):
        data = cv2.imread(str(self.files[i]))
        timestamp = Path(self.files[i]).stat().st_mtime_ns
        return ImageSample(data=bgr2rgb(data), timestamp=timestamp)

    def __repr__(self):
        return f"ImageFolder{self.files!r}"
