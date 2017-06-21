import requests
import datetime
import pika
import ssl
import json
import logging


class ClientConfig:

    @staticmethod
    def fromfile(filename):
        with open(filename) as f:
            return ClientConfig(**json.load(f))

    def __init__(self, **kwargs):
        """
        ClientConfig organizes connection and credential information associated
        to a Beehive server.
        """
        self.node = kwargs.get('node', None)
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', None)
        self.username = kwargs.get('username', 'node')
        self.password = kwargs.get('password', 'waggle')
        self.ssl_enabled = kwargs.get('ssl_enabled', None)
        self.ssl_options = {}

        if 'cacert' in kwargs:
            self.ssl_options['ca_certs'] = kwargs['cacert']

        if 'cert' in kwargs:
            self.ssl_options['certfile'] = kwargs['cert']

        if 'key' in kwargs:
            self.ssl_options['keyfile'] = kwargs['key']

        self.ssl_options['cert_reqs'] = ssl.CERT_REQUIRED

        # set default ssl_enabled, if needed
        if self.ssl_enabled is None:
            if 'ca_certs' in self.ssl_options:
                self.ssl_enabled = True
            else:
                self.ssl_enabled = False

        # set default port, if needed
        if self.port is None:
            if self.ssl_options:
                self.port = 5671
            else:
                self.port = 5672


class MessageClient:

    logger = logging.getLogger('beehive.MessageClient')

    def __init__(self, name, config, exchange='data.fanout'):
        self.name = name
        self.config = config
        self.exchange = exchange

        credentials = pika.PlainCredentials(
            username=config.username,
            password=config.password)

        self.parameters = pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=credentials,
            ssl=config.ssl_enabled,
            ssl_options=config.ssl_options,
            connection_attempts=5,
            retry_delay=5,
            socket_timeout=10)

    def connect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def disconnect(self):
        self.connection.disconnect()

    def publish(self, topic, value):
        utcnow = datetime.datetime.utcnow()
        timestamp = int(utcnow.timestamp() * 1000)

        if isinstance(value, bytes) or isinstance(value, bytearray):
            content_type = 'b'
            body = bytes(value)
        else:
            content_type = 'j'
            body = json.dumps(value, separators=(',', ':'))

        self.logger.info('publishing {} on {}'.format(body, topic))

        properties = pika.BasicProperties(
            delivery_mode=2,
            timestamp=timestamp,
            content_type=content_type,
            type=topic,
            app_id=self.name,
            user_id=self.config.username)

        # NOTE maintains compatibility for development until id is username.
        if self.config.node is not None:
            properties.reply_to = self.config.node

        self.channel.basic_publish(properties=properties,
                                   exchange=self.exchange,
                                   routing_key=topic,
                                   body=body)

    def subscribe(self, topic, callback):
        raise NotImplementedError('some day...')


class WorkerClient:

    logger = logging.getLogger('beehive.WorkerClient')

    def __init__(self, name, config):
        self.name = name
        self.config = config

        credentials = pika.PlainCredentials(
            username=config.username,
            password=config.password)

        self.parameters = pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=credentials,
            ssl=config.ssl_enabled,
            ssl_options=config.ssl_options,
            connection_attempts=5,
            retry_delay=5,
            socket_timeout=10)

    def connect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def disconnect(self):
        self.connection.disconnect()

    def add_handler(self, handler, topic=''):
        def callback(ch, method, headers, body):
            try:
                result = handler(headers.type, body)
            except KeyboardInterrupt:
                self.stop_working()
            except:
                return

            print(result)
            # self.channel.basic_ack()

        self.channel.basic_consume(callback, routing_key=topic, queue=self.name)

    def start_working(self, handler):
        self.channel.start_consuming()

    def stop_working(self):
        self.channel.stop_consuming()


class Beehive(object):

    def __init__(self, host):
        self.host = host

    def nodes(self):
        r = requests.get('http://{}/api/1/nodes?all=true'.format(self.host))

        if r.status_code != 200:
            raise RuntimeError('Could not get nodes.')

        nodes = list(r.json()['data'].values())

        for node in nodes:
            node['node_id'] = node['node_id'][-12:].lower()

        return nodes

    def datasets(self, version='2raw', after=None, before=None):
        r = requests.get('http://{}/api/datasets?version={}'.format(self.host, version))

        datasets = r.json()

        for dataset in datasets:
            dataset['date'] = datetime.datetime.strptime(dataset['date'], '%Y-%m-%d').date()

            if after is not None and dataset['date'] < after:
                continue

            if before is not None and dataset['date'] > before:
                continue

            yield dataset
