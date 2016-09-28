from datetime import datetime
import json
import pika
import time
import waggle.platform


class PluginBackend(object):

    def connect(self):
        pass

    def send(self, sensor, data):
        pass


class PluginManagerBackend(PluginBackend):

    def __init__(self, queue):
        self.queue = queue

    def connect(self):
        pass

    def send(self, sensor, data):
        now = time.time()
        timestamp_epoch = int(now * 1000)
        timestamp_utc = int(now)
        timestamp_date = time.strftime('%Y-%m-%d', time.gmtime(timestamp_utc))

        self.queue.put([
            str(timestamp_date),
            self.plugin_name,
            self.plugin_version,
            '',
            timestamp_epoch,
            sensor,
            '',
            ['data:{}'.format(data)],
        ])


class StandloneBackend(PluginBackend):

    def __init__(self, callback):
        self.callback = callback

    def connect(self):
        pass

    def send(self, sensor, data):
        self.callback(sensor, data)


class RabbitMQBackend(PluginBackend):

    def __init__(self, host='localhost'):
        self.host = host

        # NOTE I strongly dislike this and think it should be handled in a more
        # weakly coupled way. This is worth creating a better design for.
        self.node_id = waggle.platform.macaddr()

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.host))

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
            # consider packing certain types to save space.
            # can also consider automatically applying zlib
            # if it makes sense on the data. it'd be even
            # better if we could take advantage of protobufs
            # or some standard, open encoding technique.
            # data = struct.pack('>i', data)
            data = str(data).encode()
            datatype = 'i'
        elif isinstance(data, float):
            # data = struct.pack('>f', data)
            data = str(data).encode()
            datatype = 'f'
        elif isinstance(data, str):
            data = data.encode()
            datatype = 's'
        elif isinstance(data, bytearray):
            data = bytes(data)
            datatype = 'b'
        elif isinstance(data, bytes):
            datatype = 'b'
        else:
            raise ValueError('unsupported data type')

        properties = pika.BasicProperties(
            delivery_mode=2,  # persist message
            type=datatype,
            timestamp=int(time.time() * 1000),
            headers={
                'node': self.node_id,
                'plugin': [self.plugin_name, self.plugin_version, ''],
                'key': sensor,
            }
        )

        self.channel.basic_publish(properties=properties,
                                   exchange='sensor-data',
                                   routing_key='',
                                   body=data)


class Plugin(object):

    def __init__(self, backend):
        if not hasattr(self, 'plugin_name'):
            raise RuntimeError('Plugin name must be specified.')

        if not hasattr(self, 'plugin_version'):
            raise RuntimeError('Plugin version must be specified.')

        self.backend = backend
        self.backend.connect()

    def send(self, sensor, data):
        assert isinstance(sensor, str)
        self.backend.send(sensor, data)

    def run(self):
        raise NotImplemented('Plugin must define run method.')

    @classmethod
    def register(cls, name, man, mailbox_outgoing):
        backend = PluginManagerBackend(mailbox_outgoing)
        # backend = RabbitMQBackend('localhost')
        plugin = cls(backend)
        plugin.name = name
        plugin.man = man
        plugin.run()

    @classmethod
    def run_standalone(cls, callback):
        backend = StandloneBackend(callback)
        plugin = cls(backend)
        plugin.run()


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
            'node_id': '00A',
            'node_config': '123abc',
            'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        })

        self.channel.basic_publish(exchange='plugins-out',
                                   routing_key='',
                                   # routing_key='envsense.2',
                                   body=json.dumps(payload))

    def start(self):
        def callback(ch, method, properties, body):
            headers = properties.headers
            param = tuple(headers['sensor'])
            self.get_message(headers, param, body)

        self.channel.basic_consume(callback, queue=self.queue_name, no_ack=True)
        self.channel.start_consuming()
