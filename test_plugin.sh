#!/bin/bash -e

python3 -c '
from waggle.plugin import Plugin
import socket

plugin = Plugin()

for x in range(10):
    plugin.add_measurement({"id": 1, "sub_id": 2, "value": x})

plugin.publish_measurements()
'
