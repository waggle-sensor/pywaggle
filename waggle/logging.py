import logging
import pika
import time


class BeehiveHandler(logging.Handler):

    def __init__(self, url='amqp://localhost', exchange='logs'):
        logging.Handler.__init__(self)

        self.connection = pika.BlockingConnection(pika.URLParameters(url))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=exchange,
                                      exchange_type='topic',
                                      durable=True)

        self.exchange = exchange

    def emit(self, record):
        params = record.__dict__
        routing_key = '{}.{}'.format(params['name'].lower(),
                                     params['levelname'].lower())

        body = self.format(record)

        properties = pika.BasicProperties(timestamp=int(time.time() * 1000))

        self.channel.basic_publish(properties=properties,
                                   exchange=self.exchange,
                                   routing_key=routing_key,
                                   body=body)

#
#
# connection = pika.BlockingConnection(pika.URLParameters('amqp://localhost'))
#
# channel = connection.channel()
#
# channel.exchange_declare('logs',
#                          exchange_type='topic',
#                          durable=True)
#
#
# def log(topic, body):
#     properties = pika.BasicProperties(
#         timestamp=int(time.time() * 1000)
#     )
#
#     channel.basic_publish(properties=properties,
#                           exchange='logs',
#                           routing_key=topic,
#                           body=body)
