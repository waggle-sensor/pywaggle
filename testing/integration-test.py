from waggle.plugin import Plugin
import wagglemsg
import os
import pika
import time
from contextlib import ExitStack

os.environ["WAGGLE_PLUGIN_USERNAME"] = "plugin"
os.environ["WAGGLE_PLUGIN_PASSWORD"] = "plugin"
os.environ["WAGGLE_PLUGIN_HOST"] = "127.0.0.1"
os.environ["WAGGLE_PLUGIN_PORT"] = "5672"


with ExitStack() as es:
    params = pika.ConnectionParameters(credentials=pika.PlainCredentials("admin", "admin"))
    connection = es.enter_context(pika.BlockingConnection(params))
    channel = es.enter_context(connection.channel())

    # flush to-validator queue
    while True:
        ok, properties, body = channel.basic_get("to-validator", auto_ack=True)
        if ok is None:
            break

    # connect subscriber and ensure sufficient time to connect and subscribe
    subscriber = es.enter_context(Plugin())
    subscriber.subscribe("test")
    time.sleep(1)

    # publish test message
    with Plugin() as publisher:
        publisher.publish("test", 123)

    # load and forward message (this mocks out the data-sharing-service functionality)
    ok, properties, body = channel.basic_get("to-validator", auto_ack=True)
    msg = wagglemsg.load(body)
    channel.basic_publish("data.topic", msg.name, body)

    # confirm we can get the message and that it matches what we had before
    msg2 = subscriber.get(1)
    assert msg == msg2
