# Waggle Python Module

pywaggle is a Python module for implementing [Waggle](https://github.com/waggle-sensor/waggle) plugins and system services.

## Installation Guides

Most users getting started with pywaggle will want to install latest version with all optional dependencies using:

```sh
pip install -U pywaggle[all]
```

Advanced users can install specific subsets of functionality using the following extras flags:

* `audio` - Audio and microphone support for plugins.
* `vision` - Image, video and camera support for plugins.

```sh
# install only core plugin features
pip install pywaggle

# install only audio features
pip install pywaggle[audio]

# install only vision features
pip install pywaggle[vision]

# install both audio and vision features
pip install pywaggle[audio,vision]
```

## Usage Guides

* [Writing a plugin](https://github.com/waggle-sensor/pywaggle/blob/main/docs/writing-a-plugin.md)
