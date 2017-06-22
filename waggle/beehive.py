import requests
import datetime
import pika
import ssl
import logging


class ClientConfig:

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


class BaseClient:

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


class MessageClient(BaseClient):

    def publish(self, topic, body, exchange='data-pipeline-in'):
        utcnow = datetime.datetime.utcnow()
        timestamp = int(utcnow.timestamp() * 1000)

        properties = pika.BasicProperties(
            delivery_mode=2,
            timestamp=timestamp,
            type=topic,
            app_id=self.name,
            user_id=self.config.username)

        # NOTE maintains compatibility for development until id is username.
        if self.config.node is not None:
            properties.reply_to = self.config.node

        self.channel.basic_publish(
            properties=properties,
            exchange=exchange,
            routing_key=topic,
            body=body)

    def subscribe(self, topic, callback):
        raise NotImplementedError('some day...')


class WorkerClient(BaseClient):

    def add_handler(self, handler):
        def callback(ch, method, headers, body):
            try:
                result = handler(headers.type, body)
            except KeyboardInterrupt:
                self.stop_working()
            except:
                return

            self.channel.basic_ack(method.delivery_tag)
            print(result)

        self.channel.basic_consume(callback, queue=self.name)

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
