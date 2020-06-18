# Plugin Submodule

Plugins provide a simple interface for publishing sensor data to Beehive and
for processing messages sent back to a node.

## Core Plugin API

### class waggle.plugin.Plugin

This class implements a few key groups of functionality:

* Publish measurements to Beehive.
* Processing messages sent to a node.

Each of the functions are documented below.

#### Plugin()

Plugin will read the following environmental variables:

* `WAGGLE_PLUGIN_ID` **required** Plugin ID.
* `WAGGLE_PLUGIN_VERSION` **required** Plugin version `x.y.z`.
* `WAGGLE_PLUGIN_INSTANCE` **_optional_** Plugin instance. Defaults to 0.
* `WAGGLE_PLUGIN_HOST` **_optional_** RabbitMQ host. Defaults to `rabbitmq`.
* `WAGGLE_PLUGIN_PORT` **_optional_** RabbitMQ port. Defaults to `5672`.
* `WAGGLE_PLUGIN_USERNAME` **_optional_** RabbitMQ username. Defaults to `worker`.
* `WAGGLE_PLUGIN_PASSWORD` **_optional_** RabbitMQ password. Defaults to `worker`.

#### add_measurement(measurement)

Adds a measurement to the current batch to be published.

A measurement is either be a dictionary with fields:

* `id` **required** Sensor ID.
* `sub_id` **required** Sensor sub ID.
* `value` **required** Measurement value. Data type is infered from Python type.
* `inst` **_optional_** Sensor instance. Default is 0.
* `source_id` **_optional_** Hardware source ID. Default is 0.
* `source_inst` **_optional_** Hardware source instance. Default is 0.
* `timestamp` **_optional_** Seconds since epoch. Default is current time.

Or, prepacked sensorgram bytes. See the [protocol docs](https://github.com/waggle-sensor/pywaggle/tree/develop/waggle/protocol) for more information about sensorgrams and other data types.

#### publish_measurements()

Publish and empty the current batch of measurements.

#### clear_measurements()

Empty the current batch of measurements without publishing.

#### get_waiting_messages()

Enumerates messages send to the plugin.

#### publish_heartbeat()

Publish a heartbeat message. _May_ be used by node to provide software watchdog.

## Basic Example

In our first example, we prepare three synthetic measurements and publish them
to the console to make sure that our code is working.

```txt
import waggle.plugin
import time

# Initialize our test plugin.
plugin = waggle.plugin.Plugin()

while True:
    # Add our three measurements to the batch.
    plugin.add_measurement({'id': 1, 'sub_id': 0, 'value': 100})
    plugin.add_measurement({'id': 1, 'sub_id': 1, 'value': 32.1})
    plugin.add_measurement({'id': 2, 'sub_id': 0, 'value': b'blob of data'})

    # Publish the batch.
    plugin.publish_measurements()

    # Wait five seconds before repeating.
    time.sleep(5)
```

Running this should produce:

TODO: This examples will not work as-is. It currently requires runtime support from virtual waggle or a node.

```sh
$ python3 plugin
publish measurements:
{'id': 1, 'inst': 0, 'sub_id': 0, 'timestamp': 1532965991, 'value': 100}
{'id': 1, 'inst': 0, 'sub_id': 1, 'timestamp': 1532965991, 'value': 32.099998474121094}
{'id': 2, 'inst': 0, 'sub_id': 0, 'timestamp': 1532965991, 'value': b'blob of data'}
publish measurements:
{'id': 1, 'inst': 0, 'sub_id': 0, 'timestamp': 1532965996, 'value': 100}
{'id': 1, 'inst': 0, 'sub_id': 1, 'timestamp': 1532965996, 'value': 32.099998474121094}
{'id': 2, 'inst': 0, 'sub_id': 0, 'timestamp': 1532965996, 'value': b'blob of data'}
...
```
