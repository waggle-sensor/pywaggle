from distutils.core import setup

setup(
    name='waggle',
    version='0.7.0',
    description='Python Waggle Module',
    url='https://github.com/waggle-sensor/pywaggle',
    install_requires=[
        'pika',
        'crcmod',
    ],
    packages=[
        'waggle',
        'waggle.platform',
        'waggle.protocol',
        'waggle.protocol.utils',
        'waggle.coresense',
    ],
)
