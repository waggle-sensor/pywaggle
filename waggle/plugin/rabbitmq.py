import logging
from threading import Thread, Event
from queue import Queue, Empty
import time
import pika
import pika.exceptions
import wagglemsg
from .config import PluginConfig


logger = logging.getLogger(__name__)
# pika is very verbose at DEBUG level. we turn it down here.
logging.getLogger("pika").setLevel(logging.CRITICAL)


class RabbitMQPublisher:
    """
    RabbitMQPublisher manages a connection to RabbitMQ and publishes messages from the provided queue.

    This is done in a background thread which must be stopped by setting the provided stop Event.
    """

    def __init__(self, config: PluginConfig, messages: Queue, stop: Event):
        self.config = config
        self.params = get_connection_parameters_for_config(config)
        self.messages = messages
        self.stop = stop
        self.done = Event()
        Thread(target=self.__main).start()
    
    def __main(self):
        try:
            while not self.stop.is_set():
                try:
                    self.__connect_and_flush_messages()
                except Exception:
                    time.sleep(1)
        finally:
            self.done.set()

    def __connect_and_flush_messages(self):
        with pika.BlockingConnection(self.params) as conn, conn.channel() as ch:
            while not self.stop.is_set():
                self.__flush_messages(ch)
            # attempt to flush any remaining messages
            self.__flush_messages(ch)

    def __flush_messages(self, ch):
        while True:
            try:
                item = self.messages.get(timeout=1)
            except Empty:
                return

            properties = pika.BasicProperties(
                delivery_mode=2,
                user_id=self.params.credentials.username)
            
            # NOTE app_id is used by data service to validate and tag additional metadata provided by k3s scheduler.
            if self.config.app_id != "":
                properties.app_id = self.config.app_id

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("publishing message to rabbitmq: %s", wagglemsg.load(item.body))

            ch.basic_publish(
                exchange="to-validator",
                routing_key=item.scope,
                properties=properties,
                body=item.body)


class RabbitMQConsumer:
    """
    RabbitMQConsumer manages a connection to RabbitMQ and puts received messages into the provided queue.

    This is done in a background thread which must be stopped by setting the provided stop Event.
    """

    def __init__(self, topics, config: PluginConfig, messages: Queue, stop: Event):
        self.topics = topics
        self.config = config
        self.params = get_connection_parameters_for_config(config)
        self.messages = messages
        self.stop = stop
        self.done = Event()
        Thread(target=self.__main).start()

    def __main(self):
        try:
            while not self.stop.is_set():
                try:
                    self.__connect_and_consume_messages()
                except Exception:
                    time.sleep(1)
        finally:
            self.done.set()

    def __connect_and_consume_messages(self):
        with pika.BlockingConnection(self.params) as conn, conn.channel() as ch:
            # setup subscriber queue and bind to topics
            queue = ch.queue_declare("", exclusive=True).method.queue
            ch.basic_consume(queue, self.__process_message, auto_ack=True)
            ch.queue_bind(queue, "data.topic", self.topics)

            def check_stop():
                if self.stop.is_set():
                    ch.stop_consuming()
                else:
                    conn.call_later(1, check_stop)

            conn.call_later(1, check_stop)
            ch.start_consuming()
    
    def __process_message(self, ch, method, properties, body):
        try:
            msg = wagglemsg.load(body)
        except TypeError:
            logger.debug("unsupported message type: %s %s", properties, body)
            return
        self.messages.put(msg)


def get_connection_parameters_for_config(config: PluginConfig) -> pika.ConnectionParameters:
    return pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=pika.PlainCredentials(
                username=config.username,
                password=config.password,
            ),
            connection_attempts=1,
            socket_timeout=1.0,
        )
