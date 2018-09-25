# Messaging Submodule

This submodule provides an easy and reliable way to do messaging over serial
ports.

## Example

```python
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
```
