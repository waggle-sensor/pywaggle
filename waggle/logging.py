import logging
import pika
import time


class BeehiveHandler(logging.Handler):

    def __init__(self, url='amqp://localhost'):
        logging.Handler.__init__(self)

        self.url = url
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

                self.channel.exchange_declare(exchange='logs.fanout',
                                              exchange_type='fanout',
                                              durable=True)

                self.channel.queue_declare(queue='logs',
                                           durable=True)

                self.channel.queue_bind(queue='logs',
                                        exchange='logs.fanout')
            except pika.exceptions.ConnectionClosed:
                pass
            else:
                break

    def publish(self, properties, body):
        while True:
            try:
                self.channel.basic_publish(properties=properties,
                                           exchange='logs.fanout',
                                           routing_key='',
                                           body=body)
            except pika.exceptions.ConnectionClosed:
                self.connect()
            else:
                break


def getLogger(service, url='amqp://localhost', queue='logs'):
    assert isinstance(service, str)
    logger = logging.getLogger(service)
    logger.addHandler(BeehiveHandler(url=url, queue=queue))
    return logger
