from distutils.core import setup

setup(
    name='waggle',
    version='0.23.14',
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
        'waggle.plugin',
        'waggle.protocol.utils',
        'waggle.protocol.v0',
        'waggle.protocol.v3',
        'waggle.protocol.v4',
        'waggle.protocol.v5',
        'waggle.protocol.v5.utils',
        'waggle.protocol.v5.res',
        'waggle.coresense',
    ],
)
