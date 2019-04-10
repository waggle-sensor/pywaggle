# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import io

start_byte = 0x7e
end_byte = 0x7f
escape_byte = 0x7d
escape_mask = 0x20


class MessageWriter:

    def __init__(self, writer):
        self.writer = writer

    def write_message(self, msg):
        b = bytearray()

        b.append(start_byte)

        for c in msg:
            if c in [start_byte, end_byte, escape_byte]:
                b.append(escape_byte)
                b.append(c ^ escape_mask)
            else:
                b.append(c)

        b.append(end_byte)

        self.writer.write(b)


class MessageReader:

    def __init__(self, reader):
        self.reader = reader
        self.start = False

    def read_message(self, writer):
        while not self.start:
            try:
                c = self.reader.read(1)[0]
            except IndexError:
                return False

            if c == start_byte:
                self.start = True
                self.escape = False

        while self.start:
            try:
                c = self.reader.read(1)[0]
            except IndexError:
                return False

            if c == end_byte:
                self.start = False
            elif self.escape:
                writer.write(bytes([c ^ escape_mask]))
                self.escape = False
            elif c == escape_byte:
                self.escape = True
            else:
                writer.write(bytes([c]))

        return True


class Messenger:

    def __init__(self, rw, bufferSize=1024):
        self.writer = MessageWriter(rw)
        self.reader = MessageReader(rw)
        self.buffer = io.BytesIO()

    def read_message(self):
        if self.reader.read_message(self.buffer):
            b = self.buffer.getvalue()
            self.buffer = io.BytesIO()
            return b
        else:
            return None

    def read_messages(self):
        while True:
            msg = self.read_message()

            if msg is None:
                return

            yield msg

    def write_message(self, msg):
        self.writer.write_message(msg)


if __name__ == '__main__':
    message = b'hello world'
    loopback_buffer = io.BytesIO()
    messenger = Messenger(loopback_buffer)
    messenger.write_message(message)
    loopback_buffer.seek(0)
    assert messenger.read_message() == message
