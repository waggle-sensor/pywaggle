# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import waggle.protocol

sensorgrams = [
    {'id': 1, 'sub_id': 0, 'value': 10},
    {'id': 2, 'sub_id': 0, 'value': 22.1},
    {'id': 3, 'sub_id': 0, 'value': b'blob of bytes'},
    {'id': 3, 'sub_id': 1, 'value': 'string'},
    {'id': 4, 'sub_id': 0, 'value': True, 'inst': 0},
    {'id': 4, 'sub_id': 1, 'value': False, 'inst': 0},
    {'id': 4, 'sub_id': 2, 'value': None, 'inst': 1},
]

# First, we'll pack some data of many different types.
packed_sensorgrams = waggle.protocol.pack_sensorgrams(sensorgrams)

# Now, we'll unpack and print all of that data.
print(waggle.protocol.unpack_sensorgrams(packed_sensorgrams))
