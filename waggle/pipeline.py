from datetime import datetime
import json
import pika
import time
import waggle.platform
import logging


class PluginHandler(object):

    def send(self, sensor, data):
        pass


class CallbackHandler(PluginHandler):

    def __init__(self, callback):
        self.callback = callback

    def send(self, sensor, data):
        self.callback(sensor, data)


class RabbitMQHandler(PluginHandler):

    def __init__(self, url):
        self.connection = pika.BlockingConnection(pika.URLParameters(url))

        self.channel = self.connection.channel()

        self.channel.exchange_declare('data.fanout',
                                      exchange_type='fanout',
                                      durable=True)

        self.channel.queue_declare('data',
                                   durable=True)

        self.channel.queue_bind(queue='data',
                                exchange='data.fanout')

    def send(self, sensor, data):
        if isinstance(data, int):
            content_type = 'i'
            body = str(data).encode()
        elif isinstance(data, float):
            content_type = 'f'
            body = str(data).encode()
        elif isinstance(data, str):
            content_type = 's'
            body = data.encode()
        elif isinstance(data, bytearray):
            content_type = 'b'
            body = bytes(data)
        elif isinstance(data, bytes):
            content_type = 'b'
            body = data
        elif isinstance(data, dict) or isinstance(data, list):
            content_type = 'j'
            body = json.dumps(data).encode()
        else:
            raise ValueError('unsupported data type')

        properties = pika.BasicProperties(
            delivery_mode=2,
            timestamp=int(time.time() * 1000),
            content_type=content_type,
            type=sensor,
            app_id=':'.join([self.plugin.plugin_name,
                             self.plugin.plugin_version])
        )

        self.channel.basic_publish(properties=properties,
                                   exchange='data.fanout',
                                   routing_key=properties.app_id,
                                   body=body)


class Plugin(object):

    def __init__(self):
        if not hasattr(self, 'plugin_name'):
            raise RuntimeError('Plugin name must be specified.')

        if not hasattr(self, 'plugin_version'):
            raise RuntimeError('Plugin version must be specified.')

        self.node_id = waggle.platform.macaddr()

        self.logger = logging.getLogger('{}:{}'.format(self.plugin_name,
                                                       self.plugin_version))
        self.logger.setLevel(logging.INFO)

        self.handlers = []

    def add_handler(self, handler):
        handler.plugin = self
        self.handlers.append(handler)

    def send(self, sensor, data):
        assert isinstance(sensor, str)

        self.logger.info('send {} {}'.format(sensor, data))

        for handler in self.handlers:
            handler.send(sensor, data)

    def run(self):
        raise NotImplemented('Plugin must define run method.')

    @classmethod
    def register(cls, name, man, mailbox_outgoing):
        plugin = cls.defaultConfig()
        plugin.name = name
        plugin.man = man
        plugin.run()

    @classmethod
    def defaultConfig(cls):
        plugin = cls()
        plugin.add_handler(RabbitMQHandler('amqp://localhost'))
        return plugin


class Worker(object):

    def __init__(self, host='localhost'):
        if not hasattr(self, 'plugin_name'):
            raise RuntimeError('Plugin name must be specified.')

        if not hasattr(self, 'plugin_version'):
            raise RuntimeError('Plugin version must be specified.')

        self.queue_name = '.'.join([self.plugin_name, self.plugin_version])
        self.routing_key = '.'.join([self.plugin_name, self.plugin_version])

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name)

        self.channel.queue_bind(exchange='plugins-in',
                                queue=self.queue_name,
                                routing_key=self.routing_key)

    def get_message(self, headers, param, value):
        pass

    def put_message(self, headers, payload):
        payload.update({
            # this should still be the internal node id. translation to "nice"
            # id will happen in the plenario push plugin.
            # 'node_id': '00A',
            # 'node_config': '123abc',
            'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        })

        self.channel.basic_publish(exchange='plugins-out',
                                   routing_key='',
                                   body=json.dumps(payload))

    def start(self):
        def callback(ch, method, properties, body):
            headers = properties.headers
            param = tuple(headers['key'])
            self.get_message(headers, param, body)

        self.channel.basic_consume(callback, queue=self.queue_name, no_ack=True)
        self.channel.start_consuming()
