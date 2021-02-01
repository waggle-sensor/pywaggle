#!/bin/bash

if ! test -d venv; then
    python3 -m venv venv
fi

source venv/bin/activate
pip3 install -U .
python3 test_plugin.py
python3 test_protocol.py
