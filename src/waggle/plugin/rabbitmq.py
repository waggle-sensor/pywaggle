import logging
from pydoc_data.topics import topics
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
        logger.debug("publisher thread started.")
        try:
            while not self.stop.is_set():
                try:
                    self.__connect_and_flush_messages()
                except Exception:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.exception("publisher exception!")
                time.sleep(1)
        finally:
            self.done.set()
            logger.debug("publisher thread stopped.")

    def __connect_and_flush_messages(self):
        logger.debug("publisher connecting to rabbitmq...")
        with pika.BlockingConnection(self.params) as conn, conn.channel() as ch:
            while not self.stop.is_set():
                self.__flush_messages(ch)
            logger.debug("publisher stopping...")
            # attempt to flush any remaining messages
            self.__flush_messages(ch)

    def __flush_messages(self, ch):
        logger.debug("publisher flushing messages...")
        while True:
            try:
                logger.debug("publisher waiting for message...")
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
        logger.debug("consumer thread started.")
        try:
            while not self.stop.is_set():
                try:
                    self.__connect_and_consume_messages()
                except Exception:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.exception("consumer exception!")
                time.sleep(1)
        finally:
            self.done.set()
            logger.debug("consumer thread stopped.")

    def __connect_and_consume_messages(self):
        logger.debug("consumer connecting to rabbitmq...")
        with pika.BlockingConnection(self.params) as conn, conn.channel() as ch:
            # setup subscriber queue and bind to topics
            queue = ch.queue_declare("", exclusive=True).method.queue
            logger.debug("consumer binding queue %s to topics %s", queue, self.topics)
            for topic in topics:
                ch.queue_bind(queue, "data.topic", topic)

            def check_stop():
                logger.debug("consumer checking if should stop...")
                if self.stop.is_set():
                    logger.debug("consumer stopping...")
                    ch.stop_consuming()
                else:
                    conn.call_later(1, check_stop)

            logger.debug("consumer starting to process messages...")
            conn.call_later(1, check_stop)
            ch.basic_consume(queue, self.__process_message, auto_ack=True)
            try:
                ch.start_consuming()
            finally:
                logger.debug("consumer stopped processing messages.")
    
    def __process_message(self, ch, method, properties, body):
        logger.debug("consumer processing message body %s...", body)
        try:
            msg = wagglemsg.load(body)
        except TypeError:
            logger.debug("unsupported message type: %s %s", properties, body)
            return
        logger.debug("consumer putting message %s in waiting queue", msg)
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
