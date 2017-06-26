import requests
import datetime
import pika
import ssl
import json
import base64
import logging


def utctimestamp():
    utcnow = datetime.datetime.utcnow()
    return int(utcnow.timestamp() * 1000)


class ClientConfig:

    def __init__(self, host='localhost', port=None, vhost='/', username='node',
                 password='waggle', cacert=None, cert=None, key=None,
                 node=None):
        # set connection parameters
        self.host = host
        self.port = port
        self.vhost = vhost

        # set credentials
        self.username = username
        self.password = password

        # set ssl options
        self.cacert = cacert
        self.cert = cert
        self.key = key

        # set waggle parameters
        self.node = node

    @property
    def pika_parameters(self):
        credentials = pika.PlainCredentials(
            username=self.username,
            password=self.password)

        ssl_options = {'cert_reqs': ssl.CERT_REQUIRED}

        if self.cacert is not None:
            ssl_options['ca_certs'] = self.cacert

        if self.cert is not None:
            ssl_options['certfile'] = self.cert

        if self.key is not None:
            ssl_options['keyfile'] = self.key

        if self.port is not None:
            port = self.port
        elif self.cacert is not None:
            port = 5671
        else:
            port = 5672

        return pika.ConnectionParameters(
            host=self.host,
            port=port,
            virtual_host=self.vhost,
            credentials=credentials,
            ssl=self.cacert is not None,
            ssl_options=ssl_options,
            connection_attempts=5,
            retry_delay=5,
            socket_timeout=10)


class PluginClient:

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.connection = pika.BlockingConnection(config.pika_parameters)
        self.channel = self.connection.channel()

    def close(self):
        self.connection.close()

    def publish(self, topic, body, exchange='data-pipeline-in'):
        properties = pika.BasicProperties(
            delivery_mode=2,
            timestamp=utctimestamp(),
            app_id=self.name,
            user_id=self.config.username,
            type=topic)

        # NOTE maintains compatibility for development until id is username.
        if self.config.node is not None:
            properties.reply_to = self.config.node

        self.channel.basic_publish(
            properties=properties,
            exchange=exchange,
            routing_key=self.name,
            body=body)

    def subscribe(self, topic, callback):
        raise NotImplementedError('some day...')


class WorkerClient:

    logger = logging.getLogger('WorkerClient')

    def __init__(self, name, config, callback, exchange='plugins-out'):
        self.name = name
        self.config = config
        self.connection = pika.BlockingConnection(config.pika_parameters)
        self.channel = self.connection.channel()
        self.callback = callback
        self.exchange = exchange

        def wrapped_callback(ch, method, headers, body):
            doc = {
                'version': 1,
                'timestamp': headers.timestamp,
                'type': headers.type,
                'body': base64.b64encode(body).decode(),
                'encoding': 'base64',
            }

            results = callback(doc)

            doc['results_timestamp'] = utctimestamp()
            doc['results'] = results

            properties = pika.BasicProperties(
                delivery_mode=2,
                app_id=headers.app_id,
                user_id=headers.user_id,
                type=headers.type,
                content_type='json')

            json_doc = json.dumps(doc)

            self.logger.debug('publishing {}'.format(json_doc))

            self.channel.basic_publish(
                properties=properties,
                exchange=self.exchange,
                routing_key=method.routing_key,
                body=json.dumps(doc))

            self.channel.basic_ack(method.delivery_tag)

        self.channel.basic_consume(wrapped_callback, queue=self.name)

    def close(self):
        self.connection.close()

    def start_working(self):
        self.channel.start_consuming()

    def stop_working(self):
        self.channel.stop_consuming()


class Beehive:

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
