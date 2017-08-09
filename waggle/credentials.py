from configparser import ConfigParser
import os.path
import logging

logger = logging.getLogger(__name__)

CREDENTIAL_PATHS = [
    './credentials',
    '~/.waggle/credentials',
    '/etc/waggle/credentials',
]


def expandpath(p):
    return os.path.abspath(os.path.expanduser(p))


def load(profile='default'):
    for path in map(expandpath, CREDENTIAL_PATHS):
        config = ConfigParser()

        try:
            logger.debug('reading credentials file {}'.format(path))
            config.read(path)
        except FileNotFoundError:
            logger.debug('no credentials file {}'.format(path))
            continue

        try:
            logger.debug('reading profile {}'.format(profile))
            return dict(config[profile])
        except KeyError:
            logger.debug('no profile file {} in {}'.format(profile, path))
            continue

    raise RuntimeError('no profile {} found in any credentials files'.format(profile))
