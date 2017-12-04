from distutils.core import setup

setup(
    name='waggle',
    version='0.23.0',
    description='Python Waggle Module',
    url='https://github.com/waggle-sensor/pywaggle',
    install_requires=[
        'pika',
        'crcmod',
        'requests',
        'pyserial',
        'pyyaml',
        'bitstring'
    ],
    packages=[
        'waggle',
        'waggle.platform',
        'waggle.protocol.v4',
        'waggle.protocol.v5',
        'waggle.protocol.v5.utils',
        'waggle.coresense',
    ],
)
