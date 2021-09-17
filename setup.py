from setuptools import setup
from os import getenv

setup(
    name="waggle",
    version=getenv("RELEASE_VERSION", "0.0.0"),
    description="Official Waggle Python module",
    url="https://github.com/waggle-sensor/pywaggle",
    install_requires=[
        # "wagglemsg @ ..."
        "pika>=1.2.0",
        "soundcard>=0.4.1",
        "soundfile>=0.9.0",
        # "numpy",
        # "opencv-python",
    ],
    extras_require={
        "dev": [
            "numpy",
            "opencv-python"
        ],
    },
    packages=[
        "waggle",
        "waggle.data",
    ],
    python_requires=">=3.6",
)
