# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from distutils.core import setup
import waggle

setup(
    name='waggle',
    version=waggle.__version__,
    description='Python Waggle Module',
    url='https://github.com/waggle-sensor/pywaggle',
    install_requires=[
        'pika>=1.0.0',
    ],
    packages=[
        'waggle',
    ],
    include_package_data=True,
)
