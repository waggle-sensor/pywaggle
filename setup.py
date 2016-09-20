from distutils.core import setup

setup(
    name='waggle',
    version='0.1.2',
    description='Python Waggle Module',
    url='https://github.com/waggle-sensor/pywaggle',
    install_requires=[
        'pika',
    ],
    packages=[
        'waggle',
        'waggle.platform'
    ],
)
