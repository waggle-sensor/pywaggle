import os


def isimported(filename):
    name, ext = os.path.splitext(filename)
    return ext == '.py' and not name.startswith('test_')


imported = list(filter(isimported, os.listdir(os.path.dirname(__file__))))
__all__ = [filename.replace('.py', '') for filename in imported]

from . import *
