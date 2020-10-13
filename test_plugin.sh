#!/bin/bash -e

python3 -c '
import waggle.plugin as plugin
import socket

plugin.init()
plugin.publish("test", 1)
plugin.publish("test", "hello")
'
