# waggle.plugin

Plugins provide a simple interface for publishing sensor data to Beehive and
for processing messages sent back to a node.

## Plugin API

The plugin API provides a few core areas of functionality:

### Publishing Measurements

* `add_measurement(measument)` - Add measument to batch.
* `publish_measurements()` - Publish current batch of measurements.
* `clear_measurements()` - Clear current batch of measurements without publishing.

### Processing Messages

* `get_waiting_messages()` - Enumerates messages send to the plugin.

### Plugin Resilience

* `publish_heartbeat()` - Publish a heartbeat message.

## Examples

### Basic Example

In our first example, we prepare three synthetic measurements and publish them
to the console to make sure that our code is working.

```python
import waggle.plugin
import time

# Initialize our test plugin.
plugin = waggle.plugin.PrintPlugin()

while True:
  # Add our three measurements to the batch.
  plugin.add_measurement({'sensor_id': 1, 'parameter_id': 0, 'value': 100})
  plugin.add_measurement({'sensor_id': 1, 'parameter_id': 1, 'value': 32.1})
  plugin.add_measurement({'sensor_id': 2, 'parameter_id': 0, 'value': b'blob of data'})

  # Publish the batch.
  plugin.publish_measurements()

  # Wait five seconds before repeating.
  time.sleep(5)
```

Running this should produce:

```sh
$ python3 plugin
publish measurements:
{'sensor_id': 1, 'sensor_instance': 0, 'parameter_id': 0, 'timestamp': 1532965991, 'type': 20, 'value': 100}
{'sensor_id': 1, 'sensor_instance': 0, 'parameter_id': 1, 'timestamp': 1532965991, 'type': 30, 'value': 32.099998474121094}
{'sensor_id': 2, 'sensor_instance': 0, 'parameter_id': 0, 'timestamp': 1532965991, 'type': 0, 'value': b'blob of data'}
publish measurements:
{'sensor_id': 1, 'sensor_instance': 0, 'parameter_id': 0, 'timestamp': 1532965996, 'type': 20, 'value': 100}
{'sensor_id': 1, 'sensor_instance': 0, 'parameter_id': 1, 'timestamp': 1532965996, 'type': 30, 'value': 32.099998474121094}
{'sensor_id': 2, 'sensor_instance': 0, 'parameter_id': 0, 'timestamp': 1532965996, 'type': 0, 'value': b'blob of data'}
...
```

### Development, Testing and Deployment

To facilitate development and testing, we used a "print out" implementation of
the plugin interface. In our example above, this was chosen during the step:

```python
# Initialize our test plugin.
plugin = waggle.plugin.PrintPlugin()
```

Once we get plugin code working and ready for deployment, we'll instead use:

```python
# Initialize our real plugin.
plugin = waggle.plugin.Plugin()
```

This version is implemented on top of the local data cache so that published
data can be forwarded to Beehive.

### Complete Measurement Reference

Our `add_measurement` example only covered the most common usage. For a
complete reference, please see the [section on sensorgrams](https://github.com/waggle-sensor/pywaggle/tree/develop/waggle/protocol/README.md#sensorgram-operations) in the [protocol docs](https://github.com/waggle-sensor/pywaggle/tree/develop/waggle/protocol/README.md).
