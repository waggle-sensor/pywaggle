# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from distutils.core import setup
import waggle
import unittest

setup(
    name="waggle",
    version=waggle.__version__,
    description="Official Waggle Python module",
    url="https://github.com/waggle-sensor/pywaggle",
    install_requires=[
        "pika>=1.2.0",
        "soundcard>=0.4.1",
        "soundfile>=0.9.0",
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
