import argparse
from protocol import pack_sensorgram, unpack_sensorgram
from protocol import pack_sensorgrams, unpack_sensorgrams
from serial import Serial
from base64 import b64encode, b64decode
import binascii
import sys
import time


class Connection:

    def __init__(self, port):
        self.ser = Serial(port, 115200, timeout=1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def send(self, sg):
        self.ser.write(b64encode(pack_sensorgram(sg)))
        self.ser.write(b'\n')

    def recv(self):
        # needs global timeout too
        while True:
            line = self.ser.readline()

            if len(line) == 0:
                return None

            try:
                return unpack_sensorgrams(b64decode(line.strip()))
            except (binascii.Error, IndexError):
                print('skip', line.strip())

    def recv_all(self):
        while True:
            msgs = c.recv()
            if msgs is None:
                return
            yield from msgs


parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()


with Connection(args.port) as c:
    while True:
        print('requesting status')
        c.send({'id': 1, 'sub_id': 1, 'value': 1})
        c.send({'id': 2, 'sub_id': 1, 'value': 1})
        c.send({'id': 3, 'sub_id': 1, 'value': 1})
        c.send({'id': 4, 'sub_id': 1, 'value': 1})
        c.send({'id': 10, 'sub_id': 1, 'value': 1})

        for msg in c.recv_all():
            print('recv', msg)

        print('start all')
        c.send({'id': 5, 'sub_id': 1, 'value': 0})
        c.send({'id': 5, 'sub_id': 1, 'value': 1})
        c.send({'id': 5, 'sub_id': 1, 'value': 2})
        c.send({'id': 5, 'sub_id': 1, 'value': 3})
        c.send({'id': 5, 'sub_id': 1, 'value': 4})
        time.sleep(3)

        for msg in c.recv_all():
            print('recv', msg)

        print('stop all')
        c.send({'id': 6, 'sub_id': 1, 'value': (0, 0)})
        c.send({'id': 6, 'sub_id': 1, 'value': (1, 0)})
        c.send({'id': 6, 'sub_id': 1, 'value': (2, 0)})
        c.send({'id': 6, 'sub_id': 1, 'value': (3, 0)})
        c.send({'id': 6, 'sub_id': 1, 'value': (4, 0)})
        time.sleep(3)

        for msg in c.recv_all():
            print('recv', msg)

        time.sleep(3)
