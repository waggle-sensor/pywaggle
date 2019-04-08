# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import waggle.protocol

# We'll do a more involved example, where we pack and unpack a datagram with
# a body of sensorgrams.

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

print('--- datagram bytes')
print(data)

# Now, we'll unpack all of this.
datagram = waggle.protocol.unpack_datagram(data)
sensorgrams = waggle.protocol.unpack_sensorgrams(datagram['body'])

print('--- datagram')
print(datagram)

print('--- sensorgrams')
print(sensorgrams)
