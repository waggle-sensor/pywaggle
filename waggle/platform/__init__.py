import re
import subprocess


def read_file(path):
    with open(path) as file:
        return file.read()


def hardware():
    match = re.search('ODROID-?(.*)', read_file('/proc/cpuinfo'))
    model = match.group(1)
    if model.startswith('C'):
        return 'C1+'
    if model.startswith('XU'):
        return 'XU4'
    raise RuntimeError('Unknown hardware.')


def macaddr():
    output = subprocess.check_output(['ip', 'link']).decode()
    match = re.search(r'link/ether (00:1e:06:\S+)', output)
    return match.group(1).replace(':', '').rjust(16, '0')
