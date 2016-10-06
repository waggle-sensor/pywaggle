from datetime import datetime
import json
import pika
import time
import waggle.platform
import logging


logging.basicConfig()


class PluginHandler(object):

    def send(self, sensor, data):
        pass


class PluginManagerHandler(PluginHandler):

    def __init__(self, queue):
        self.queue = queue

    def send(self, sensor, data):
        now = time.time()
        timestamp_epoch = int(now * 1000)
        timestamp_utc = int(now)
        timestamp_date = time.strftime('%Y-%m-%d', time.gmtime(timestamp_utc))

        self.queue.put([
            str(timestamp_date),
            self.plugin.plugin_name,
            self.plugin.plugin_version,
            '',
            timestamp_epoch,
            sensor,
            '',
            ['data:{}'.format(data)],
        ])


class CallbackHandler(PluginHandler):

    def __init__(self, callback):
        self.callback = callback

    def send(self, sensor, data):
        self.callback(sensor, data)


class LogHandler(PluginHandler):

    def send(self, sensor, data):
        print('{} - {} - {}'.format(time.time(), sensor, data))


class RabbitMQHandler(PluginHandler):

    def __init__(self, url):
        self.connection = pika.BlockingConnection(pika.URLParameters(url))

        self.channel = self.connection.channel()

        self.channel.exchange_declare('sensor-data',
                                      exchange_type='fanout',
                                      durable=True)

        self.channel.queue_declare(queue='sensor-data',
                                   durable=True)

        self.channel.queue_bind(exchange='sensor-data',
                                queue='sensor-data')

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
        else:
            raise ValueError('unsupported data type')

        properties = pika.BasicProperties(
            delivery_mode=2,
            timestamp=int(time.time() * 1000),
            content_type=content_type,
            type=sensor,
            app_id='.'.join([self.plugin.plugin_name,
                             self.plugin.plugin_version])
        )

        self.channel.basic_publish(properties=properties,
                                   exchange='sensor-data',
                                   routing_key='',
                                   body=body)


class Plugin(object):

    def __init__(self):
        if not hasattr(self, 'plugin_name'):
            raise RuntimeError('Plugin name must be specified.')

        if not hasattr(self, 'plugin_version'):
            raise RuntimeError('Plugin version must be specified.')

        # NOTE I strongly dislike this and think it should be handled in a more
        # weakly coupled way. This is worth creating a better design for.
        try:
            self.node_id = waggle.platform.macaddr()
        except:
            self.node_id = None

        self.handlers = []

    def add_handler(self, handler):
        handler.plugin = self
        self.handlers.append(handler)

    def send(self, sensor, data):
        assert isinstance(sensor, str)

        for handler in self.handlers:
            handler.send(sensor, data)

    def run(self):
        raise NotImplemented('Plugin must define run method.')

    @classmethod
    def register(cls, name, man, mailbox_outgoing):
        plugin = cls()

        plugin.add_handler(LogHandler())

        # Legacy plugin manager handler + parameters.
        plugin.name = name
        plugin.man = man

        try:
            plugin.add_handler(RabbitMQHandler('amqp://localhost'))
        except:
            logging.exception('Got exception when adding RabbitMQ handler.')
            # Use old pipeline instead.
            plugin.add_handler(PluginManagerHandler(mailbox_outgoing))

        plugin.run()

    @classmethod
    def defaultConfig(cls):
        plugin = cls()
        plugin.add_handler(LogHandler())
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
