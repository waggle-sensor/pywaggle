import re


cache = dict()


def hardware():
    if 'hardware' not in cache:
        cache['hardware'] = detect_hardware()
    return cache['hardware']


def detect_hardware():
    with open('/proc/cpuinfo') as f:
        match = re.search('ODROID-?(.*)', f.read())
        model = match.group(1)
        if model.startswith('C'):
            return 'C1+'
        if model.startswith('XU'):
            return 'XU4'
        raise RuntimeError('Unknown hardware.')
