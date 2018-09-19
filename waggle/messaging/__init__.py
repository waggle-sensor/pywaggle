import io

startByte = 0x7e
endByte = 0x7f
escapeByte = 0x7d
escapeMask = 0x20


class MessageWriter:

    def __init__(self, writer):
        self.writer = writer

    def writeMessage(self, msg):
        b = bytearray()

        b.append(startByte)

        for c in msg:
            if c in [startByte, endByte, escapeByte]:
                b.append(escapeByte)
                b.append(c ^ escapeMask)
            else:
                b.append(c)

        b.append(endByte)

        self.writer.write(b)


class MessageReader:

    def __init__(self, reader):
        self.reader = reader
        self.start = False

    def readMessage(self, writer):
        while not self.start:
            try:
                c = self.reader.read(1)[0]
            except IndexError:
                return False

            if c == startByte:
                self.start = True
                self.escape = False

        while self.start:
            try:
                c = self.reader.read(1)[0]
            except IndexError:
                return False

            if c == endByte:
                self.start = False
            elif self.escape:
                writer.write(bytes([c ^ escapeMask]))
                self.escape = False
            elif c == escapeByte:
                self.escape = True
            else:
                writer.write(bytes([c]))

        return True


class Messenger:

    def __init__(self, rw, bufferSize=1024):
        self.writer = MessageWriter(rw)
        self.reader = MessageReader(rw)
        self.buffer = io.BytesIO()

    def readMessage(self):
        if self.reader.readMessage(self.buffer):
            b = self.buffer.getvalue()
            self.buffer = io.BytesIO()
            return b
        else:
            return None

    def writeMessage(self, msg):
        self.writer.writeMessage(msg)
