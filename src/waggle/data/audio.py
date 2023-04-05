from os import PathLike
from pathlib import Path
import numpy
import soundfile
from typing import NamedTuple
import random
from base64 import b64encode
from io import BytesIO
from .timestamp import get_timestamp


class AudioSample(NamedTuple):
    data: numpy.ndarray
    samplerate: int
    timestamp: int

    def save(self, path: PathLike):
        path = Path(path)
        soundfile.write(str(path), self.data, self.samplerate)

    def _repr_html_(self):
        with BytesIO() as buf:
            soundfile.write(
                buf, self.data, self.samplerate, format="flac", closefd=False
            )
            b64data = b64encode(buf.getvalue()).decode()
        return f"""
<audio controls="controls" autobuffer="autobuffer">
<source src="data:audio/wav;base64,{b64data}" />
</audio>
"""


class Microphone:
    def __init__(self, samplerate=48000, channels=1, name=None):
        import soundcard

        self.microphone = soundcard.default_microphone()
        self.samplerate = samplerate
        self.channels = channels
        self.name = name

    def record(self, duration):
        timestamp = get_timestamp()
        data = self.microphone.record(
            samplerate=self.samplerate,
            numframes=int(duration * self.samplerate),
            channels=self.channels,
        )
        return AudioSample(data, self.samplerate, timestamp=timestamp)


class AudioFolder:
    available_formats = {"." + s.lower() for s in soundfile.available_formats().keys()}

    def __init__(self, root, shuffle=False):
        self.files = sorted(
            p.absolute()
            for p in Path(root).glob("*")
            if p.suffix in self.available_formats
        )
        if shuffle:
            random.shuffle(self.files)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        data, samplerate = soundfile.read(str(self.files[i]), always_2d=True)
        timestamp = Path(self.files[i]).stat().st_mtime_ns
        return AudioSample(data, samplerate, timestamp=timestamp)

    def __repr__(self):
        return f"AudioFolder{self.files!r}"
