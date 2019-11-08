from protocol import pack_sensorgram, unpack_sensorgram
from serial import Serial
from base64 import b64encode, b64decode
import binascii
import sys
import time
import queue
from threading import Thread


# handle response returns
resp = queue.Queue(1)


def hello():
    for i in range(100):
        print(i)
        try:
            resp.put(i, timeout=1)
        except queue.Full:
            print('resp timed out')


Thread(target=hello).start()

while True:
    time.sleep(3)

# with Serial(sys.argv[1], 9600, timeout=3) as ser:
#     while True:
#         sg = {
#             'timestamp': int(time.time()),
#             'id': 2222,
#             'inst': 33,
#             'sub_id': 44,
#             'source_id': 5555,
#             'source_inst': 66,
#             'value': [7, 88, 9999],
#         }
#         encoded = b64encode(pack_sensorgram(sg))

#         print('>>> sending test sensorgram')
#         print(sg)
#         print(encoded.decode())
#         ser.write(encoded)
#         ser.write(b'\n')
#         print()

#         print('>>> printing output')

#         while True:
#             line = ser.readline()
#             if len(line) == 0:
#                 break
#             print(line.strip().decode())

#             try:
#                 data = b64decode(line.strip())
#                 sg = unpack_sensorgram(data)
#                 print('sensorgram from device')
#                 print(sg)
#             except (binascii.Error, IndexError):
#                 pass

#         print()
