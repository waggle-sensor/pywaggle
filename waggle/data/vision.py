import cv2
from pathlib import Path
import numpy
from typing import NamedTuple
from contextlib import contextmanager
import time

# TODO use format spec like rgb vs bgr in config file

class ImageSample(NamedTuple):
    data: numpy.ndarray

    def save(self, filename):
        cv2.imwrite(filename, self.data)


class ImageFolder:

    available_formats = {".jpg", ".jpeg", ".png"}

    def __init__(self, root):
        self.files = sorted(p.absolute() for p in Path(root).glob("*") if p.suffix in self.available_formats)

    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, i):
        data = cv2.imread(str(self.files[i]))
        return ImageSample(data)

    def __repr__(self):
        return f"ImageFolder{self.files!r}"


class CameraFromFolder:

    available_formats = {".jpg", ".jpeg", ".png"}

    def __init__(self, root):
        self.files = sorted(p.absolute() for p in Path(root).glob("*") if p.suffix in self.available_formats)
        self.creation_time = time.time()
    
    def snapshot(self):
        index = int(time.time() - self.creation_time) % len(self.files)
        data = cv2.imread(str(self.files[index]))
        return ImageSample(data)

    def stream(self):
        for file in self.files:
            data = cv2.imread(str(file))
            yield ImageSample(data)


class CameraFromVideoFile:

    def __init__(self, filename):
        self.filename = filename
        self.capture = cv2.VideoCapture(filename)
    
    def snapshot(self):
        ok, frame = self.capture.read()
        if not ok:
            raise RuntimeError("failed to take snapshot")
        return ImageSample(frame)

    def stream(self):
        while True:
            ok, frame = self.capture.read()
            if not ok:
                break
            yield ImageSample(frame)

# TODO(sean) evaluate whether we want to be able to target different resource types using a type: prefix.
# Camera(name="dev:bottom") <- nice because allows devices to be swapped out as args
# Camera(name="file:/")

class Camera:

    @classmethod
    def from_image_folder(cls, root):
        return CameraFromFolder(root)

    @classmethod
    def from_video_file(cls, filename):
        return CameraFromVideoFile(filename)

    @classmethod
    def from_webcam(cls):
        return Camera()

    def __init__(self, name=None):
        if name is None:
            self.device = 0
        else:
            raise NotImplementedError("still need to implement looking up camera by name")

    def snapshot(self):
        with VideoCapture(self.device) as capture:
            # drop first few frames to improve exposure
            for _ in range(5):
                capture.read()
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("failed to take snapshot")
            return ImageSample(frame)

    def stream(self):
        with VideoCapture(self.device) as capture:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                yield ImageSample(frame)


@contextmanager
def VideoCapture(device):
    capture = cv2.VideoCapture(device)
    if not capture.isOpened():
        raise RuntimeError(f"unable to open video capture for device {device!r}")
    try:
        yield capture
    finally:
        capture.release()
