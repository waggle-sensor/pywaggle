# pywaggle.plugin

Plugins provide a simple interface for publishing sensor data to Beehive and
for processing messages sent back to a node.

## API

The current API can be broken down into a few core areas.

### Publishing Measurements

* `add_measurement(measument)` - Add measument to batch.
* `publish_measurements()` - Publish current batch of measurements.
* `clear_measurements()` - Clear current batch of measurements without publishing.

### Processing Messages

* `get_waiting_messages()` - Enumerates messages send to the plugin.

## Examples

### Basic Example

In our first example, we prepare three synthetic measurements and publish them
to the console to make sure that our code is working.

```python
import waggle.plugin

# Initialize our test plugin.
plugin = waggle.plugin.PrintPlugin()

# Add our three measurements to the batch.
plugin.add_measurement({'sensor_id': 1, 'parameter_id': 0, 'value': 100})
plugin.add_measurement({'sensor_id': 1, 'parameter_id': 1, 'value': 32.1})
plugin.add_measurement({'sensor_id': 2, 'parameter_id': 0, 'value': b'blob of data'})

# Publish the batch.
plugin.publish_measurements()
```

### Development, Testing and Deployment

To facilitate developing and testing, we used a "print out" implementation of
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
