import logging
import pika
import time
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

        self.url = url
        self.connect()

    def emit(self, record):
        params = record.__dict__

        body = self.format(record)

        headers = {
            'name': params['name'],
            'level': params['levelname'].lower(),
            'value': params['levelno'],
        }

        properties = pika.BasicProperties(
            timestamp=int(time.time() * 1000),
            delivery_mode=2,
            headers=headers
        )

        self.publish(properties, body)

    def connect(self):
        parameters = pika.URLParameters(self.url)

        for attempt in range(5):
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                self.channel.exchange_declare(exchange='logs.fanout',
                                              exchange_type='fanout',
                                              durable=True)

                self.channel.queue_declare(queue='logs',
                                           durable=True)

                self.channel.queue_bind(queue='logs',
                                        exchange='logs.fanout')
            except pika.exceptions.ConnectionClosed:
                time.sleep(1)
            else:
                break
        else:
            raise RuntimeError('could not connect')

    def publish(self, properties, body):
        for attempt in range(3):
            try:
                self.channel.basic_publish(properties=properties,
                                           exchange='logs.fanout',
                                           routing_key='',
                                           body=body)
            except pika.exceptions.ConnectionClosed:
                self.connect()
            else:
                break
        else:
            raise RuntimeError('could not publish')


def getLogger(service, url='amqp://localhost'):
    assert isinstance(service, str)
    logger = logging.getLogger(service)
    logger.addHandler(BeehiveHandler(url=url))
    return logger
