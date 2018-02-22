from distutils.core import setup

setup(
    name='waggle',
    version='0.23.3',
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
        'waggle.protocol.utils',
        'waggle.protocol.v4',
        'waggle.protocol.v5',
        'waggle.protocol.v5.utils',
        'waggle.protocol.v5.res',
        'waggle.coresense',
    ],
)
