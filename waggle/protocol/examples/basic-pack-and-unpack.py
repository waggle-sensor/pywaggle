import waggle.protocol

# We'll make up some test sensor values to pack. Noticed the variety of value
# types which are supported.
sensorgrams = [
  {'sensor_id': 1, 'parameter_id': 0, 'value': 10},
  {'sensor_id': 2, 'parameter_id': 0, 'value': 22.1},
  {'sensor_id': 3, 'parameter_id': 0, 'value': b'blob of bytes'},
  {'sensor_id': 3, 'parameter_id': 1, 'value': 'string'},
  {'sensor_id': 4, 'parameter_id': 0, 'value': True, 'sensor_instance': 0},
  {'sensor_id': 4, 'parameter_id': 1, 'value': False, 'sensor_instance': 0},
  {'sensor_id': 4, 'parameter_id': 2, 'value': None, 'sensor_instance': 1},
]

# First, we'll pack some data of many different types.
data = waggle.protocol.pack_sensorgrams(sensorgrams)

# Now, we'll unpack and print all of that data.
print(waggle.protocol.unpack_sensorgrams(data))