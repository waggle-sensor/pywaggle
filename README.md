# Waggle Python Module

pywaggle is a Python module for implementing [Waggle](https://github.com/waggle-sensor/waggle) plugins and system services.

## Installation Guides

Most users getting started with pywaggle will want to install latest version with all optional dependencies using:

```sh
git clone https://github.com/waggle-sensor/pywaggle
pip install ./pywaggle[all]
```

Advanced users can install specific subsets of functionality using the following extras flags:

* `audio` - Audio and microphone support for plugins.
* `vision` - Image, video and camera support for plugins.

```sh
# install only core plugin features
pip install ./pywaggle

# install only audio features
pip install ./pywaggle[audio]

# install only vision features
pip install ./pywaggle[vision]

# install both audio and vision features (same as all)
pip install ./pywaggle[audio,vision]
```

A fixed version of this module may also be included in a `requirements.txt` file using the following syntax:

```txt
waggle[all] @ https://github.com/waggle-sensor/pywaggle/releases/download/0.46.0/waggle-0.46.0-py3-none-any.whl
```

All versions can be found under the [releases page](https://github.com/waggle-sensor/pywaggle/releases).

## Usage Guides

* [Writing a plugin](./docs/writing-a-plugin.md)
