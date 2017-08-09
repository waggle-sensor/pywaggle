from configparser import ConfigParser
import os.path

CREDENTIAL_PATHS = [
    './credentials',
    '~/.waggle/credentials',
    '/etc/waggle/credentials',
]


def load(profile='default'):
    config = ConfigParser()

    for path in CREDENTIAL_PATHS:
        try:
            config.read(os.path.expanduser(path))
            return dict(config[profile])
        except FileNotFoundError:
            continue

    raise RuntimeError('no credentials file found')
