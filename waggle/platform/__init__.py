import re
import subprocess


def cached(func):
    def cachedfunc():
        if not hasattr(cachedfunc, 'value'):
            cachedfunc.value = func()
        return cachedfunc.value
    return cachedfunc


def first(p, s):
    return next(filter(p, iter(s)))


@cached
def hardware():
    with open('/proc/cpuinfo') as f:
        match = re.search('ODROID-?(.*)', f.read())
        model = match.group(1)
        if model.startswith('C'):
            return 'C1+'
        if model.startswith('XU'):
            return 'XU4'
        raise RuntimeError('Unknown hardware.')


@cached
def macaddr():
    output = subprocess.check_output(['ip', 'link']).decode()
    addrs = re.findall('link/ether (\S+)', output)
    return first(lambda m: m.startswith('00:1e:06'), addrs).replace(':', '')
