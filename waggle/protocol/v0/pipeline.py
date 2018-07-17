#!/usr/bin/env python3
import logging
import os
import pika
import secrets
from waggle.protocol.v0 import *


class Plugin:

    def __init__(self, credentials=None):
        self.logger = logging.getLogger('pipeline.Plugin')

        if credentials is None:
            username, password = os.environ['WAGGLE_PLUGIN_CREDENTIALS'].split(':')
        else:
            username, password = credentials

        self.user_id = username
        self.run_id = secrets.randbelow(0xffffffff)
        self.queue = 'in-{}'.format(username)

        credentials = pika.credentials.PlainCredentials(
            username=username,
            password=password)

        parameters = pika.ConnectionParameters(
            credentials=credentials,
            virtual_host='node1')

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.queue_declare(
            queue=self.queue,
            durable=True)

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
