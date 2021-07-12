# Waggle Python Module

![CI/CD](https://github.com/waggle-sensor/pywaggle/workflows/CI/CD/badge.svg)

pywaggle is a Python module for implementing [Waggle](https://github.com/waggle-sensor/waggle) plugins and system services.

## Installation Guides

pywaggle requires Python 3.6 or later. To install core pywaggle module, please run:

```sh
pip3 install git+https://github.com/waggle-sensor/pywaggle
```

pywaggle provides the following additional functionality if these modules are installed:

* [opencv-python](https://pypi.org/project/opencv-python). Allows loading of image / video data.

The latest version pywaggle with all optional dependencies can be installed using:

```sh
git clone https://github.com/waggle-sensor/pywaggle
pip install ./pywaggle[dev]
```

## Usage Guides

* [Writing a plugin](./docs/writing-a-plugin.md)
