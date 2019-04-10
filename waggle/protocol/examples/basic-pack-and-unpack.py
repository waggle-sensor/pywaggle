# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import waggle.protocol

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
packed_sensorgrams = waggle.protocol.pack_sensorgrams(sensorgrams)

# Now, we'll unpack and print all of that data.
print(waggle.protocol.unpack_sensorgrams(packed_sensorgrams))
