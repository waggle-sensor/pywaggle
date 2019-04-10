# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
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
