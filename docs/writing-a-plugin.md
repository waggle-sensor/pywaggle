# Writing a plugin

In this guide, we'll walk through writing a basic plugin and exploring some of the functionality provided by pywaggle.

That being said, we do want to emphasize that pywaggle is designed to make it easy to interface _existing_ Python code with the [Waggle](https://github.com/waggle-sensor/waggle) stack. To a first approximation, pywaggle aims to augment print statements with publish statements.

## What is a plugin?

A plugin is a self-contained program which typically reads sensors, audio or video data, does some processing and finally publishes results derived from that data.

<img width="600px" src="./images/plugin-overview.svg">

The most basic example of a plugin is one which simply reads and publishes a values from a sensor. A more complex plugin could publish the number of cars seen in a video stream using a deep learning model.

## Basic example

We'll start by writing a plugin which simply publishes the value 123 as
measurement `my_sensor_value` every second.

```python
from waggle import plugin
from time import sleep

plugin.init()

while True:
    sleep(1)
    print("publishing a value!")
    plugin.publish("my_sensor_value", 123)
```

Let's walk through the pywaggle related details. First, import our the pywaggle
plugin module:

```python
from waggle import plugin
```

Next, we need to initialize our plugin. This will prepare our plugin to interface
with Waggle system services.

```python
plugin.init()
```

Finally, we have our publish statement. This will queue up our measurement name and
value along with the current timestamp.

```python
plugin.publish("my_sensor_value", 123)
```

## More about the publish function

In the previous example, we saw the most basic usage of the publish function. Now, we want to talk about a couple additional features available to you.

First, metadata can be added to measurements to provide context to how a measurement was created. For example, suppose we had a left and a right facing camera on a node and wanted to track which one was used.

```python
plugin.publish("my_sensor_value", 123, meta={"camera": "left"})
```

This will bind the meta data together with the measurement and will be available throughout the rest of the data pipeline.

Second, you can explicitly provide a timestamp for situations where you have more information on when a measurement was taken. For example:

```python
plugin.publish("my_sensor_value", 123, timestamp=my_timestamp_in_ns)
```

_Note: Timestamps are expected to be in nanoseconds._

## Seeing the internal details

If we run the basic example, the only thing we'll see is the message "publishing a value!" every second. If you need to see more details, pywaggle is design to easily interface with Python's standard logging module. To enable debug logging, simply make the following additions:

```python
from waggle import plugin
from time import sleep

# 1. import standard logging module
import logging

# 2. enable debug logging
logging.basicConfig(level=logging.DEBUG)

plugin.init()

while True:
    sleep(1)
    print("publishing a value!")
    plugin.publish("my_sensor_value", 123)
```

You should see a lot of information like:

```text
DEBUG:waggle.plugin:starting plugin worker thread
DEBUG:waggle.plugin:connecting to rabbitmq broker at rabbitmq:5672 with username "plugin"
DEBUG:waggle.plugin:rabbitmq connection error: [Errno 8] nodename nor servname provided, or not known
publishing a value!
DEBUG:waggle.plugin:adding message to outgoing queue: Message(name='my_sensor_value', value=123, timestamp=1619628240863845000, meta={})
DEBUG:waggle.plugin:connecting to rabbitmq broker at rabbitmq:5672 with username "plugin"
DEBUG:waggle.plugin:rabbitmq connection error: [Errno 8] nodename nor servname provided, or not known
publishing a value!
```

The most important lines are:

```text
publishing a value!
DEBUG:waggle.plugin:adding message to outgoing queue: Message(name='my_sensor_value', value=123, timestamp=1619628240863845000, meta={})
```

These are telling us that our messages are being queued up in an outgoing queue to be shipped.

You'll also see a number of messages related to rabbitmq.

These are simply indicating the our plugin is waiting to connect to the Waggle ecosystem. This is normal when testing a standalone plugin without the rest of the Waggle stack. Plugin will simply queue up measurements in-memory until they exit.
