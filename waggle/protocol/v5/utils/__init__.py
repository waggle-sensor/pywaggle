# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import os


def isimported(filename):
    name, ext = os.path.splitext(filename)
    return ext == '.py' and not name.startswith('test_')


imported = list(filter(isimported, os.listdir(os.path.dirname(__file__))))
__all__ = [filename.replace('.py', '') for filename in imported]

from . import *
