import waggle.protocol

# First, we'll pack and unpack a generic datagram.
datagram = {
    'timestamp': 1234567,
    'plugin_id': 2,
    'plugin_major_version': 3,
    'plugin_minor_version': 5,
    'plugin_patch_version': 7,
    'plugin_instance': 11,
    'body': b'some data body here',
}

packed_datagram = waggle.protocol.pack_datagram(datagram)
print(packed_datagram)

# Now, we can combine the datagram and sensorgram functions.

body = waggle.protocol.pack_sensorgrams([
    {'sensor_id': 1, 'parameter_id': 0, 'value': b'first'},
    {'sensor_id': 2, 'parameter_id': 0, 'value': b'second'},
    {'sensor_id': 3, 'parameter_id': 0, 'value': b'third'},
])

data = waggle.protocol.pack_datagram({
    'timestamp': 1234567,
    'plugin_id': 2,
    'plugin_major_version': 3,
    'plugin_minor_version': 5,
    'plugin_patch_version': 7,
    'plugin_instance': 11,
    'body': body,
})
