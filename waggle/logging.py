import pika
import time


connection = pika.BlockingConnection(pika.URLParameters('amqp://localhost'))

channel = connection.channel()

channel.exchange_declare('logs',
                         exchange_type='topic',
                         durable=True)


def log(topic, body):
    properties = pika.BasicProperties(
        timestamp=int(time.time() * 1000)
    )

    channel.basic_publish(properties=properties,
                          exchange='logs',
                          routing_key=topic,
                          body=body)
