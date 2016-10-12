import logging
import pika
import time


class BeehiveHandler(logging.Handler):

    def __init__(self, url='amqp://localhost', queue='logs'):
        logging.Handler.__init__(self)

        self.url = url
        self.queue = queue
        self.connect()

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

        self.publish(properties, body)

    def connect(self):
        parameters = pika.URLParameters(self.url)

        while True:
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
            except pika.exceptions.ConnectionClosed:
                pass
            else:
                break

    def publish(self, properties, body):
        while True:
            try:
                self.channel.basic_publish(properties=properties,
                                           exchange='',
                                           routing_key=self.queue,
                                           body=body)
            except pika.exceptions.ConnectionClosed:
                self.connect()
            else:
                break


def getLogger(service, url='amqp://localhost', queue='logs'):
    logger = logging.getLogger(service)
    logger.addHandler(BeehiveHandler(url=url, queue=queue))
    return logger
