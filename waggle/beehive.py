import requests
import datetime
import pika
import ssl
import json
import base64
import logging
import configparser
import os
import os.path


def load_profile(name):
    config = configparser.ConfigParser()

    path = os.path.expanduser(os.environ.get('WAGGLE_PROFILES_FILE', '~/.waggle/profiles'))
    config.read(path)
    profile = config[name]

    # override using environmental parameters
    default_host = os.environ.get('WAGGLE_BEEHIVE_HOST', 'localhost')
    default_port = os.environ.get('WAGGLE_BEEHIVE_PORT', '5671')
    default_virtual_host = os.environ.get('WAGGLE_BEEHIVE_VIRTUAL_HOST', '/')
    default_username = os.environ.get('WAGGLE_BEEHIVE_USERNAME', 'node')
    default_password = os.environ.get('WAGGLE_BEEHIVE_PASSWORD', 'waggle')
    default_cacert = os.environ.get('WAGGLE_BEEHIVE_CACERT', '/usr/lib/waggle/SSL/waggleca/cacert.pem')

    # get parameters from profiles entry
    host = profile.get('beehive_host', default_host)
    port = int(profile.get('beehive_port', default_port))
    virtual_host = profile.get('beehive_virtual_host', default_virtual_host)
    username = profile.get('beehive_username', default_username)
    password = profile.get('beehive_password', default_password)
    cacert = profile.get('beehive_cacert', default_cacert)

    return {
        'host': host,
        'port': port,
        'virtual_host': virtual_host,
        'username': username,
        'password': password,
        'cacert': cacert,
    }


class Publisher:

    def __init__(self, name, profile_name='default'):
        profile = load_profile(profile_name)

        self.parameters = pika.ConnectionParameters(
            host=profile['host'],
            port=profile['port'],
            virtual_host=profile['virtual_host'],
            credentials=pika.PlainCredentials(
                username=profile['username'],
                password=profile['password'],
            ),
            connection_attempts=5,
            retry_delay=5.0,
            socket_timeout=10.0,
            ssl=True,
            ssl_options={
                'cert_reqs': ssl.CERT_REQUIRED,
                'ca_certs': profile['cacert'],
            },
        )

        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def publish(self):
        pass


def utctimestamp():
    """
    Gets number of milliseconds since epoch.
    """
    utcnow = datetime.datetime.utcnow()
    return int(utcnow.timestamp() * 1000)


def build_connection_parameters(config):
    """
    Builds connection parameters from config dictionary.
    """
    ssl_options = {
        'cert_reqs': ssl.CERT_REQUIRED,
        'ca_certs': config['cacert'],
    }

    if 'cert' in config or 'key' in config:
        ssl_options['certfile'] = config['cert']
        ssl_options['keyfile'] = config['key']

    return pika.ConnectionParameters(
        host=config.get('host', None),
        port=config.get('port', None),
        virtual_host=config.get('vhost', None),
        credentials=pika.PlainCredentials(
            username=config.get('username', None),
            password=config.get('password', None),
        ),
        connection_attempts=5,
        retry_delay=5.0,
        socket_timeout=10.0,
        ssl=True,
        ssl_options=ssl_options,
    )


def pack_message(message):
    properties = pika.BasicProperties(
        timestamp=message['timestamp'],
    )

    body = message['body']

    return {
        'properties': properties,
        'exchange': '',
        'routing_key': '',
        'body': body,
    }


def unpack_message(properties, body):
    return {
        'timestamp': properties.timestamp,
        'body': body,
    }


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
            password=self.password,
        )

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
            socket_timeout=10,
        )


class PluginClient:

    def __init__(self, name, config):
        self.name = name
        self.config = config
        # self.parameters = build_connection_parameters(config)
        self.connection = pika.BlockingConnection(self.config.pika_parameters)
        self.channel = self.connection.channel()

    def close(self):
        self.connection.close()

    def publish(self, topic, body, exchange='data-pipeline-in'):
        properties = pika.BasicProperties(
            delivery_mode=2,
            timestamp=utctimestamp(),
            app_id=self.name,
            user_id=self.config.username,
            type=topic,
        )

        # NOTE maintains compatibility for development until id is username.
        if self.config.node is not None:
            properties.reply_to = self.config.node

        return self.channel.basic_publish(
            properties=properties,
            exchange=exchange,
            routing_key=self.name,
            body=body,
        )

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
