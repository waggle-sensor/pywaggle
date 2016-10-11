import logging
import pika
import time


class BeehiveHandler(logging.Handler):

    def __init__(self, url='amqp://localhost', queue='logs'):
        logging.Handler.__init__(self)

        self.connection = pika.BlockingConnection(pika.URLParameters(url))

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue,
                                   durable=True)

        self.queue = queue

    def emit(self, record):
        params = record.__dict__

        body = self.format(record)

        headers = {
            'name': params['name'],
            'level': params['levelname'].lower(),
            'value': params['levelno'],
        }

        properties = pika.BasicProperties(
            timestamp=int(time.time() * 1000),
            delivery_mode=2,
            headers=headers
        )

        self.channel.basic_publish(properties=properties,
                                   exchange='',
                                   routing_key=self.queue,
                                   body=body)
