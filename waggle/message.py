import base64
import json
from typing import NamedTuple, Any


class Message(NamedTuple):
    name: str
    value: Any
    timestamp: int
    meta: dict


def dump(msg: Message) -> bytes:
    # pack metadata into standard amqp message properties
    tmpval = msg.value
    enc = ""
    if isinstance(msg.value, (bytes, bytearray)):
        enc = "b64"
        tmpval = base64.b64encode(msg.value).decode()

    return json.dumps({
        "name": msg.name,
        "ts": msg.timestamp,
        "val": tmpval,
        "meta": msg.meta,
	    "enc": enc
    }, separators=(",", ":"))


def load(body: bytes) -> Message:
    data = json.loads(body)

    if data["enc"] == "b64":
        data["val"] = base64.b64decode(data["val"])

    return Message(
        name=data["name"],
        value=data["val"],
        timestamp=data["ts"],
        meta=data["meta"])
