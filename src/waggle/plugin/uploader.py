import hashlib
import json
from pathlib import Path
from shutil import copyfile
from .time import get_timestamp


class Uploader:
    def __init__(self, root):
        self.root = Path(root)

    # NOTE uploads are stored in the following directory structure:
    # root/
    #   timestamp-sha1sum/
    #     data
    #     meta
    def upload_file(self, path, meta={}, timestamp=None, keep=False):
        # get timestamp before doing other work
        timestamp = timestamp or get_timestamp()

        path = Path(path)
        checksum = sha1sum_for_file(path)

        # create upload dir
        upload_dir = Path(self.root, f"{timestamp}-{checksum}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # stage data file
        # NOTE we do a copy instead of move, as the upload dir may
        # be mounted from another disk.
        copyfile(path, Path(upload_dir, "data"))
        if not keep:
            path.unlink()

        # stage meta file
        metafile = {
            "timestamp": timestamp,
            "shasum": checksum,
            "labels": {k: v for k, v in meta.items()},
        }
        metafile["labels"]["filename"] = path.name
        write_json_file(Path(upload_dir, "meta"), metafile)

        return upload_dir


def sha1sum_for_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(32768)
            if chunk == b"":
                break
            h.update(chunk)
    return h.hexdigest()


def write_json_file(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, separators=(",", ":"), sort_keys=True)
