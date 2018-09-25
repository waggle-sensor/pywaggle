#!/usr/bin/env python3
from serial import Serial
from waggle.messaging import Messenger


def run_messenger_example(messenger):
    while True:
        # write a hello message
        messenger.writeMessage(b'hello!')

        # attempt to read a single message
        msg = messenger.readMessage()

        if msg is not None:
            print('got message', msg)

        # attempt to read all waiting messages
        for msg in messenger.readMessages():
            print('got message', msg)


def main():
    with Serial('/dev/my-device', timeout=1.0) as ser:
        run_messenger_example(Messenger(ser))


if __name__ == '__main__':
    main()
