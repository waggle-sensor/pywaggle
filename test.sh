#!/bin/bash

# run tests on local waggle/ directory
python3 -m unittest discover -s tests

# to run tests on installed package, use:
# (cd tests && python3 -m unittest discover)
