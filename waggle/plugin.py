#!/usr/bin/env python3
import logging
import os
import pika
import waggle.protocol.v0 as protocol


class Plugin:

    def __init__(self, credentials=None):
        self.logger = logging.getLogger('pipeline.Plugin')

        parameters = pika.URLParameters(get_rabbitmq_url())
        self.user_id = parameters.credentials.username
        self.queue = 'to-{}'.format(self.user_id)

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.measurements = []

    def publish(self, body):
        self.logger.debug('Publishing message data %s.', body)

        self.channel.basic_publish(
            exchange='publish',
            routing_key='',
            properties=pika.BasicProperties(
                delivery_mode=2,
                user_id=self.user_id),
            body=body)

    def get_waiting_messages(self):
        self.channel.queue_declare(queue=self.queue, durable=True)

        while True:
            method, properties, body = self.channel.basic_get(queue=self.queue)

            if body is None:
                break

            self.logger.debug('Yielding message data %s.', body)
            yield body

            self.logger.debug('Acking message data.')
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def add_measurement(self, sensorgram):
        """Add a measument to measurement queue.

        This function accepts both dict and bytes type objects.

        dict objects support the following keys:
        sensor_id -- sensor ID
        parameter_id -- parameter ID
        value -- raw sensor value bytes
        sensor_instance -- sensor instance (default 0)
        timestamp -- time measurement was taken (default now in seconds)

        These objects will be packed and added to the publishing buffer upon
        calling this function.

        Example:
        plugin.add_measurement({
            'sensor_id': 2,
            'parameter_id': 3,
            'value': b'some register values',
        })

        bytes objects should be in the standard packed sensorgram format. These
        will be published without modification.

        Example:
        data = read_sensorgram_bytes_from_serial_port()
        plugin.add_measurement(data)
        """
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        """Clear measurement queue without publishing."""
        self.measurements.clear()

    def publish_measurements(self):
        """Publish and clear the measurement queue."""
        data = b''.join(self.measurements)

        message = protocol.pack_message({
            'body': protocol.pack_datagram({
                'body': data
            })
        })

        self.publish(message)
        self.clear_measurements()


def get_rabbitmq_url():
    return os.environ.get('WAGGLE_PLUGIN_RABBITMQ_URL', 'amqp://localhost')


class PrintPlugin:

    def __init__(self):
        self.measurements = []

    def publish(self, body):
        print('publish', body)

    def get_waiting_messages(self):
        return

    def add_measurement(self, sensorgram):
        self.measurements.append(pack_measurement(sensorgram))

    def clear_measurements(self):
        """Clear measurement queue without publishing."""
        self.measurements.clear()

    def publish_measurements(self):
        """Publish and clear the measurement queue."""
        data = b''.join(self.measurements)

        message = protocol.unpack_message(protocol.pack_message({
            'body': protocol.pack_datagram({
                'body': data
            })
        }))

        datagram = protocol.unpack_datagram(message['body'])
        sensorgrams = protocol.unpack_sensorgrams(datagram['body'])

        print('publish measurements:')

        for sensorgram in sensorgrams:
            print(sensorgram)

        self.clear_measurements()


def pack_measurement(sensorgram):
    if isinstance(sensorgram, (bytes, bytearray)):
        return sensorgram
    if isinstance(sensorgram, dict):
        return protocol.pack_sensorgram(sensorgram)
    raise ValueError('Sensorgram must be bytes or dict.')


# def infer_measurement_type(sensorgram):
#     sensorgram = sensorgram.copy()
#
#     # check if type exists already and use that if it does?
#
#     # otherwise, infer from value type
#     if isinstance(sensorgram['value'], (bytes, bytearray)):
#         sensorgram['type'] = 0
#     elif isinstance(sensorgram['value'], int):
#         sensorgram['type']
