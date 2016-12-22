from datetime import datetime
import json
import pika
import time
import waggle.platform
import logging
import os.path

class Dependency(object):

    def check(self):
        raise NotImplemented('Dependency must define check method that returns True/False.')

class FileExistDependency(Dependency):
    def __init__(self, arg):
        self.target = arg

    def check(self):
        if isinstance(self.target, list):
            ret = [os.path.exists(t) for t in target]
            if all(ret):
                return True
            return False

        return os.path.exists(self.target)

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
        self.dest_exchange = dest_queue + '.fanout'
        self.connection = pika.BlockingConnection(pika.URLParameters(url))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(self.dest_exchange,
                                      exchange_type='fanout',
                                      durable=True)

        self.channel.queue_declare(dest_queue,
                                   durable=True)

        self.channel.queue_bind(queue=dest_queue,
                                exchange=self.dest_exchange)

    def send(self, sensor, data, headers={}):
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
            app_id=':'.join([self.plugin.plugin_name,
                             self.plugin.plugin_version])
        )

        self.channel.basic_publish(properties=properties,
                                   exchange=self.dest_exchange,
                                   routing_key=properties.app_id,
                                   body=body)

class Plugin(object):

    def __init__(self):
        if not hasattr(self, 'plugin_name'):
            raise RuntimeError('Plugin name must be specified.')

        if not hasattr(self, 'plugin_version'):
            raise RuntimeError('Plugin version must be specified.')

        # NOTE I strongly dislike this and think it should be handled in a more
        # weakly coupled way. This is worth creating a better design for.
        self.headers = {}
        try:
            self.headers['node_id'] = waggle.platform.macaddr()
            self.headers['platform'] = waggle.platform.hardware()
        except:
            pass

        self.logger = logging.getLogger('{}:{}'.format(self.plugin_name,
                                                       self.plugin_version))
        self.logger.setLevel(logging.INFO)

        self.handlers = []
        self.fileHandlers = []
        self.dependencies = []

    def add_handler(self, handler):
        handler.plugin = self
        self.handlers.append(handler)

    def add_file_handler(self, handler):
        handler.plugin = self
        self.fileHandlers.append(handler)

    def add_dependency(self, dep):
        self.dependencies.append(dep)

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
            hdr['ext'] =  splt[1]
            hdr['size'] = len(binary)

            for handler in self.fileHandlers:
                handler.send(sensor, binary, headers=hdr)

        except Exception as e:
            self.logger.info('Error while sending file:{}'.format(str(e)))
            return False

        return True

    def start(self, check_period=1):
        self.logger.info('Starting...')
        while True:
            try:
                checks = [i.check() for i in self.dependencies]
                if all(checks):
                    self.run()
                else:
                    time.sleep(check_period)
            except Exception as e:
                self.logger.error('on_start:%s' % str(e))
                self.logger.info('Restarting in %d...' % check_period)
                time.sleep(check_period)

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
