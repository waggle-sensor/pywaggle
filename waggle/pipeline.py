# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from datetime import datetime
import json
import pika
import time
import waggle.platform
import logging
import os.path


logger = logging.getLogger('waggle.pipeline')

logger.warning(
    'waggle.pipeline is deprecated. Please see the new '
    'waggle.plugin docs for the new interface: '
    'https://github.com/waggle-sensor/pywaggle/blob/master/waggle/plugin/README.md'
)


class PluginHandler(object):

    def send(self, sensor, data, headers={}):
        pass


class CallbackHandler(PluginHandler):

    def __init__(self, callback):
        self.callback = callback

    def send(self, sensor, data, headers={}):
        self.callback(sensor, data)


class RabbitMQHandler(PluginHandler):

    def __init__(self, url, dest_queue='data'):
        self.dest_queue = dest_queue
        self.dest_exchange = dest_queue + '.fanout'

        self.parameters = pika.URLParameters(url)

        # override reconnect parameters
        self.parameters.connection_attempts = 5
        self.parameters.retry_delay = 5.0
        self.parameters.socket_timeout = 2.0
        self._connect()

    def _connect(self):

        self.connection = pika.BlockingConnection(self.parameters)

        self.channel = self.connection.channel()

        # ensure that destination queues and exchanges are configured
        self.channel.exchange_declare(
            self.dest_exchange,
            exchange_type='fanout',
            durable=True
        )

        self.channel.queue_declare(self.dest_queue, durable=True)

        self.channel.queue_bind(queue=self.dest_queue, exchange=self.dest_exchange)

    def send(self, sensor, data, headers={}, reconnect_attempt=2):
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
            headers=headers,
            delivery_mode=2,
            timestamp=int(time.time() * 1000),
            content_type=content_type,
            type=sensor,
            app_id=self.plugin.id,
        )

        for i in range(reconnect_attempt + 1):
            try:
                self.channel.basic_publish(
                    properties=properties,
                    exchange=self.dest_exchange,
                    routing_key=properties.app_id,
                    body=body
                )
                return True
            except pika.exceptions.ConnectionClosed:
                self._connect()
            except Exception as ex:
                if self.channel.is_open:
                    self.channel.close()
                if self.connection.is_open:
                    self.channel.close()
                self._connect()
            time.sleep(1)
        return False


class ImagePipelineHandler(object):
    def __init__(self, routing_in, url='amqp://localhost', exchange='image_pipeline'):
        self.connection = None
        self.channel = None
        self.exchange = exchange
        self.routing_in = routing_in

        self.parameters = pika.URLParameters(url)

        # override reconnect parameters
        self.parameters.connection_attempts = 5
        self.parameters.retry_delay = 5.0
        self.parameters.socket_timeout = 2.0
        self._connect()

    def _connect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type='direct',
            durable=True
        )
        result = self.channel.queue_declare(exclusive=True, arguments={'x-max-length': 1})
        self.in_queue = result.method.queue
        self.channel.queue_bind(
            queue=self.in_queue,
            exchange=self.exchange,
            routing_key=self.routing_in
        )

    def close(self):
        try:
            if self.channel is not None:
                if self.channel.is_open:
                    self.channel.close()
            if self.connection is not None:
                if self.connection.is_open:
                    self.connection.close()
        except Exception:
            pass

    def raw_read(self):
        return self.channel.basic_get(queue=self.in_queue, no_ack=True)

    def read(self, timeout=5):
        for i in range(timeout):
            try:
                method, properties, body = self.channel.basic_get(queue=self.in_queue, no_ack=True)
                if method is not None:
                    return True, (properties, body)
            except pika.exceptions.ConnectionClosed:
                self._connect()
            except Exception as ex:
                return False, str(ex)
            time.sleep(1)
        return False, ''

    def write(self, to, frame, headers, reconnect_attempt=2):
        if not isinstance(frame, bytes):
            raise ValueError('unsupported data type')

        properties = pika.BasicProperties(
            headers=headers,
            delivery_mode=2,
            timestamp=int(time.time() * 1000),
            content_type='b',
        )
        for i in range(reconnect_attempt + 1):
            try:
                self.channel.basic_publish(
                    properties=properties,
                    exchange=self.exchange,
                    routing_key=to,
                    body=frame
                )
                return True
            except pika.exceptions.ConnectionClosed:
                self._connect()
            except Exception as ex:
                if self.channel.is_open:
                    self.channel.close()
                if self.connection.is_open:
                    self.channel.close()
                self._connect()
            time.sleep(1)
        return False


class Plugin(object):

    def __init__(self):
        if not hasattr(self, 'plugin_name'):
            raise RuntimeError('Plugin name must be specified.')

        if not hasattr(self, 'plugin_version'):
            raise RuntimeError('Plugin version must be specified.')

        id_fields = [
            self.plugin_name,
            self.plugin_version,
        ]

        if hasattr(self, 'plugin_instance'):
            id_fields.append(self.plugin_instance)

        self.id = ':'.join(id_fields)

        # NOTE I strongly dislike this and think it should be handled in a more
        # weakly coupled way. This is worth creating a better design for.
        self.headers = {}

        try:
            self.headers['node_id'] = waggle.platform.macaddr()
            self.headers['platform'] = waggle.platform.hardware()
        except Exception:
            pass

        self.logger = logging.getLogger(self.id)
        self.logger.setLevel(logging.INFO)

        self.handlers = []
        self.fileHandlers = []

    def add_handler(self, handler):
        handler.plugin = self
        self.handlers.append(handler)

    def add_file_handler(self, handler):
        handler.plugin = self
        self.fileHandlers.append(handler)

    def send(self, sensor, data):
        assert isinstance(sensor, str)

        self.logger.info('send {} {}'.format(sensor, data))

        for handler in self.handlers:
            handler.send(sensor, data, headers=self.headers)

    def send_file(self, sensor, filepath):
        assert isinstance(sensor, str)
        assert isinstance(filepath, str)

        self.logger.info('send {} {}'.format(sensor, filepath))

        try:
            if not os.path.isfile(filepath):
                self.logger.info('Error:{} does not exist'.format(filepath))
                return False
            binary = b''
            with open(filepath, 'rb') as f:
                binary = f.read()
            filename = os.path.basename(filepath)
            splt = os.path.splitext(filename)

            hdr = {}
            hdr.update(self.headers)
            hdr['fname'] = splt[0]
            hdr['ext'] = splt[1]
            hdr['size'] = len(binary)

            for handler in self.fileHandlers:
                handler.send(sensor, binary, headers=hdr)

        except Exception as e:
            self.logger.info('Error while sending file:{}'.format(str(e)))
            return False

        return True

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

    @classmethod
    def fileTransferConfig(cls):
        plugin = cls()
        plugin.add_handler(RabbitMQHandler('amqp://localhost'))
        plugin.add_file_handler(RabbitMQHandler('amqp://localhost', dest_queue='images'))
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
