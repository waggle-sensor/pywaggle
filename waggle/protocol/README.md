# waggle.protocol

This package provides functionality for packing and unpacking the various
protocols used by the Waggle platform.

## Core Data Types

The Waggle platform implements a variety of data types, each used for a specific
layer of the message pipeline. The typical data flow looks like:

1. Plugin publishes **sensorgrams**.
2. Node bundles **sensorgrams** and plugin info into **datagram**.
3. Node bundles **datagrams** with sender and receiver info into **waggle message**.

The resulting waggle message, depicted visually, would be organized like:

```
+-------------------------+
| waggle message          |
| sender-info: node123    |
| receiver-info: beehive  |
| datagrams:              |
| +---------------------+ |
| | datagram 1          | |
| | plugin-info: sysmon | |
| | sensorgrams:        | |
| | +---------------+   | |
| | | measurement 1 |   | |
| | | measurement 2 |   | |
| | | ...           |   | |
| | | measurement n |   | |
| | +---------------+   | |
| +---------------------+ |
| ...more datagrams...    |
+-------------------------+
```

### Sensorgram

Sensorgrams capture information about a measurement. Specifically, they provide
support for:

* Timestamp
* Sensor ID
* Sensor Instance
* Parameter ID
* Value
* Value Type

### Datagram

### Waggle Message

## Protocol API

The protocol API provides a few core areas of functionality:

### Sensorgram packing / unpacking

* `pack_sensorgrams(sensorgrams) -> data`
* `unpack_sensorgrams(data) -> sensorgrams`

A sensorgram is provided as a dictionary with the following items:

Required:

* `sensor_id` - Sensor ID.
* `parameter_id` - Parameter ID.
* `value`: Measurement value.

Optional:

* `timestamp` - Seconds since epoch. Defaults is current time.
* `sensor_instance` - Sensor instance. Defaults is 0.
* `type` - Value type. Default automatically derived from value's Python type.

Example:

```python
# First, we'll pack some data of many different types.
data = pack_sensorgrams([
  {'sensor_id': 1, 'parameter_id': 0, 'value': 10},
  {'sensor_id': 2, 'parameter_id': 0, 'value': 22.1},
  {'sensor_id': 3, 'parameter_id': 0, 'value': b'blob of bytes'},
  {'sensor_id': 3, 'parameter_id': 1, 'value': 'string'},
  {'sensor_id': 4, 'parameter_id': 0, 'value': True, 'sensor_instance': 0},
  {'sensor_id': 4, 'parameter_id': 1, 'value': False, 'sensor_instance': 0},
  {'sensor_id': 4, 'parameter_id': 2, 'value': None, 'sensor_instance': 1},
])

# Now, we'll unpack and print all of that data.
print(unpack_sensorgrams(data))
```
