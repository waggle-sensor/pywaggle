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
        if isinstance(sensorgram, (bytes, bytearray)):
            data = sensorgram
        elif isinstance(sensorgram, dict):
            data = protocol.pack_sensorgram(sensorgram)
        else:
            raise ValueError('Sensorgram must be bytes or dict.')

        self.measurements.append(data)

    def clear_measurements(self):
        self.measurements.clear()

    def publish_measurements(self):
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
