#!/bin/bash -e

# BUG This test relies on the internal detail that Plugin gets it's
# env config before connecting to RabbitMQ. This is bad!
#
# What this leads to is expecting the config step to pass and then
# the connection to fail, hence the except socket.gaierror.
test_plugin_env() {
    # check for ennvironmental dependencies
    WAGGLE_PLUGIN_ID=1 \
    WAGGLE_PLUGIN_VERSION=1.2.3 \
    WAGGLE_NODE_ID=0000000000000000 \
    WAGGLE_SUB_ID=0000000000000000 \
    python3 -c '
from waggle.plugin import Plugin
import socket

try:
    Plugin()
except socket.gaierror:
    pass
'
}

test_plugin_env
