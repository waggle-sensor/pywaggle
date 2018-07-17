#!/usr/bin/env python3
import logging
import os
import pika
import random
from waggle.protocol.v0 import unpack_waggle_packets


class Plugin:

    def __init__(self, credentials=None):
        self.logger = logging.getLogger('pipeline.Plugin')

        rabbitmq_url = os.environ.get('WAGGLE_PLUGIN_RABBITMQ_URL', 'amqp://localhost')
        parameters = pika.URLParameters(rabbitmq_url)

        self.user_id = parameters.credentials.username
        self.run_id = random.randint(0, 0xffffffff-1)
        self.queue = 'in-{}'.format(self.user_id)

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue, durable=True)

    def publish(self, body):
        self.logger.debug('Publishing message %s', body)

        self.channel.basic_publish(
            exchange='publish',
            routing_key='',
            properties=pika.BasicProperties(
                delivery_mode=2,
                user_id=self.user_id),
            body=body)

    def get_waiting_messages(self):
        while True:
            method, properties, body = self.channel.basic_get(queue=self.queue)

            if body is None:
                break

            for message in unpack_waggle_packets(body):
                yield message

            self.channel.basic_ack(delivery_tag=method.delivery_tag)
