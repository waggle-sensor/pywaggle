import logging
import pika
import time
import waggle.platform
import sys
import requests
import json


def getpriority(levelno):
    if levelno <= 10:
        return 7  # debug
    elif levelno <= 20:
        return 5  # notice
    elif levelno <= 30:
        return 4  # warning
    elif levelno <= 40:
        return 3  # error
    else:
        return 2  # critical


def getroutingkey(levelno):
    if levelno <= 10:
        return 'debug'
    elif levelno <= 20:
        return 'info'
    elif levelno <= 30:
        return 'warn'
    elif levelno <= 40:
        return 'error'
    else:
        return 'crit'


class JournalHandler(logging.Handler):

    def emit(self, record):
        params = record.__dict__
        levelno = params['levelno']
        msg = params['msg']

        sys.stdout.write('<{}>{}\n'.format(getpriority(levelno), msg))
        sys.stdout.flush()


def getemoji(levelno):
    if levelno >= 40:
        return ':exclamation:'
    elif levelno >= 30:
        return ':warning:'
    else:
        return ':speech_balloon:'


class SlackHandler(logging.Handler):

    def __init__(self, url):
        logging.Handler.__init__(self)
        self.url = url

    def emit(self, record):
        params = record.__dict__
        name = params['name']
        levelno = params['levelno']
        msg = params['msg']

        data = {
            'username': name,
            'text': '{} {}'.format(getemoji(levelno), msg),
        }

        requests.post(self.url, data=json.dumps(data))


class BeehiveHandler(logging.Handler):

    def __init__(self, url='amqp://localhost'):
        logging.Handler.__init__(self)

        self.parameters = pika.URLParameters(url)

        # override reconnect parameters
        self.parameters.connection_attempts = 5
        self.parameters.retry_delay = 2.5
        self.parameters.socket_timeout = 2.5

        try:
            self.model = waggle.platform.hardware()
            self.macaddr = waggle.platform.macaddr()
        except:
            self.model = ''
            self.macaddr = ''

        self.connection = pika.BlockingConnection(self.parameters)

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='logs.fanout',
                                      exchange_type='fanout',
                                      durable=True)

        self.channel.queue_declare(queue='logs',
                                   durable=True)

        self.channel.queue_bind(queue='logs',
                                exchange='logs.fanout')

    def emit(self, record):
        params = record.__dict__

        body = self.format(record)

        headers = {
            'platform': self.model,
            'node_id': self.macaddr,
            'name': params['name'],
            'level': params['levelname'].lower(),
            'value': params['levelno'],
        }

        properties = pika.BasicProperties(timestamp=int(time.time() * 1000),
                                          delivery_mode=2,
                                          headers=headers)

        self.publish(properties, body)

    def publish(self, properties, body, routing_key=''):
        self.channel.basic_publish(properties=properties,
                                   exchange='logs.fanout',
                                   routing_key=routing_key,
                                   body=body)


def getLogger(service, url='amqp://localhost'):
    logger = logging.getLogger(service)
    logger.addHandler(BeehiveHandler(url=url))
    return logger
