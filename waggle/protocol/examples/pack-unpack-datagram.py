import waggle.protocol

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
