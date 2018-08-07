import re
import subprocess


def read_file(path):
    with open(path) as file:
        return file.read()


def hardware():
    return scan_hardware(read_file('/proc/cpuinfo'))


def scan_hardware(s):
    match = re.search('ODROID-?(.*)', s)
    model = match.group(1)
    if model.startswith('C'):
        return 'C1+'
    if model.startswith('XU'):
        return 'XU4'
    raise RuntimeError('Unknown hardware.')


def macaddr():
    return scan_macaddr(subprocess.check_output(['ip', 'link']).decode())


def scan_macaddr(s):
    match = re.search(r'link/ether (00:1e:06:\S+)', s)
    return match.group(1).replace(':', '').rjust(16, '0')


def node_id():
    return macaddr()
