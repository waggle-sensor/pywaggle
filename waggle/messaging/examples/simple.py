#!/usr/bin/env python3
# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from serial import Serial
from waggle.messaging import Messenger


def run_messenger_example(messenger):
    while True:
        # write a hello message
        messenger.write_message(b'hello!')

        # attempt to read a single message
        msg = messenger.read_message()

        if msg is not None:
            print('got message', msg)

        # attempt to read all waiting messages
        for msg in messenger.read_messages():
            print('got message', msg)


def main():
    with Serial('/dev/my-device', timeout=1.0) as ser:
        run_messenger_example(Messenger(ser))


if __name__ == '__main__':
    main()
