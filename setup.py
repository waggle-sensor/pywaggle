from setuptools import setup
from os import getenv

setup(
    name="waggle",
    version=getenv("RELEASE_VERSION", "0.0.0"),
    description="Official Waggle Python module",
    url="https://github.com/waggle-sensor/pywaggle",
    install_requires=[
        "wagglemsg @ https://github.com/waggle-sensor/pywagglemsg/releases/download/0.1.0/wagglemsg-0.1.0-py3-none-any.whl",
        "pika>=1.2.0",
        "soundcard>=0.4.1",
        "soundfile>=0.9.0",
        "numpy",
        "opencv-python",
    ],
    packages=[
        "waggle",
        "waggle.data",
    ],
    python_requires=">=3.6",
)
