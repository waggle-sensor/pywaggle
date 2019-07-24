# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from distutils.core import setup

setup(
    name='waggle',
    version='0.28.0',
    description='Python Waggle Module',
    url='https://github.com/waggle-sensor/pywaggle',
    install_requires=[
        'pika>=1.0.0',
        'crcmod',
        'requests',
        'pyserial',
        'pyyaml',
        'bitstring'
    ],
    packages=[
        'waggle',
        'waggle.messaging',
        'waggle.platform',
        'waggle.plugin',
        'waggle.protocol',
        'waggle.protocol.utils',
        'waggle.protocol.v0',
        'waggle.protocol.v3',
        'waggle.protocol.v4',
        'waggle.protocol.v5',
        'waggle.protocol.v5.utils',
        'waggle.protocol.v5.res',
        'waggle.coresense',
    ],
    include_package_data=True,
)
