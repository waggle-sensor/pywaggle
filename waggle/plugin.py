#!/usr/bin/env python3
import logging
import os
import pika
import random


class Plugin:

    def __init__(self, credentials=None):
        self.logger = logging.getLogger('pipeline.Plugin')

        self.run_id = generate_run_id()

        parameters = pika.URLParameters(get_rabbitmq_url())
        self.user_id = parameters.credentials.username
        self.queue = 'to-{}'.format(self.user_id)

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

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


def get_rabbitmq_url():
    return os.environ.get('WAGGLE_PLUGIN_RABBITMQ_URL', 'amqp://localhost')


def generate_run_id():
    return random.randint(0, 0xffffffff - 1)
