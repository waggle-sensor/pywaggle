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
* `WAGGLE_PLUGIN_INSTANCE` **optional** Plugin instance. Defaults to 0.
* `WAGGLE_PLUGIN_HOST` **optional** RabbitMQ host. Defaults to `rabbitmq`.
* `WAGGLE_PLUGIN_PORT` **optional** RabbitMQ port. Defaults to `5672`.
* `WAGGLE_PLUGIN_USERNAME` **optional** RabbitMQ username. Defaults to `worker`.
* `WAGGLE_PLUGIN_PASSWORD` **optional** RabbitMQ password. Defaults to `worker`.

#### add_measurement(measurement)

Adds a measurement to the current batch to be published.

A measurement is either be a dictionary with fields:

* `id` **required** Sensor ID.
* `sub_id` **required** Sensor sub ID.
* `value` **required** Measurement value. Data type is infered from Python type.
* `inst` **optional** Sensor instance. Default is 0.
* `source_id` **optional** Hardware source ID. Default is 0.
* `source_inst` **optional** Hardware source instance. Default is 0.
* `timestamp` **optional** Seconds since epoch. Default is current time.

Or, prepacked sensorgram bytes. See the [protocol docs](https://github.com/waggle-sensor/pywaggle/tree/develop/waggle/protocol) for more information about sensorgrams and other data types.

#### publish_measurements()

Publish and empty the current batch of measurements.

#### clear_measurements()

Empty the current batch of measurements without publishing.

#### get_waiting_messages()

Enumerates messages send to the plugin.

#### publish_heartbeat()

Publish a heartbeat message. _May_ be used by node to provide software watchdog.

### class waggle.plugin.PrintPlugin

This class provides the same interface as waggle.plugin.Plugin, but will print
results to the console instead of interacting with the message pipeline.

It is intended for local development and testing without requiring a full node
environment.

## Basic Example

In our first example, we prepare three synthetic measurements and publish them
to the console to make sure that our code is working.

```python
import waggle.plugin
import time

# Initialize our test plugin.
plugin = waggle.plugin.Plugin()

while True:
    # Add our three measurements to the batch.
    plugin.add_measurement({'sensor_id': 1, 'sub_id': 0, 'value': 100})
    plugin.add_measurement({'sensor_id': 1, 'sub_id': 1, 'value': 32.1})
    plugin.add_measurement({'sensor_id': 2, 'sub_id': 0, 'value': b'blob of data'})

    # Publish the batch.
    plugin.publish_measurements()

    # Wait five seconds before repeating.
    time.sleep(5)
```

Running this should produce:

```sh
$ python3 plugin
publish measurements:
{'sensor_id': 1, 'sensor_instance': 0, 'sub_id': 0, 'timestamp': 1532965991, 'type': 20, 'value': 100}
{'sensor_id': 1, 'sensor_instance': 0, 'sub_id': 1, 'timestamp': 1532965991, 'type': 30, 'value': 32.099998474121094}
{'sensor_id': 2, 'sensor_instance': 0, 'sub_id': 0, 'timestamp': 1532965991, 'type': 0, 'value': b'blob of data'}
publish measurements:
{'sensor_id': 1, 'sensor_instance': 0, 'sub_id': 0, 'timestamp': 1532965996, 'type': 20, 'value': 100}
{'sensor_id': 1, 'sensor_instance': 0, 'sub_id': 1, 'timestamp': 1532965996, 'type': 30, 'value': 32.099998474121094}
{'sensor_id': 2, 'sensor_instance': 0, 'sub_id': 0, 'timestamp': 1532965996, 'type': 0, 'value': b'blob of data'}
...
```

## Advanced Example

Additional plugin connection info can be specified through the Credentials
object. For example, we can connect directly to a beehive server as a specific
node assuming we have the SSL files.

```python
credentials = waggle.plugin.Credentials(
    host='my-beehive',
    node_id='0000000000000001',
    sub_id='0000000000000002',
    cacert='/path/to/cacert.pem',
    cert='/path/to/cert.pem',
    key='/path/to/key.pem')

plugin = waggle.plugin.Plugin(
    id=37,
    version=(1, 0, 0),
    credentials=credentials)
```
