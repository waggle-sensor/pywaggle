from serial import Serial
import time


class TimedTransport(object):

    def __init__(self, device, baudrate, device_timeout=60, packet_timeout=5):
        self.serial = Serial(device, baudrate, timeout=0)
        self.device_timeout = device_timeout
        self.packet_timeout = packet_timeout

    def wait_for_data(self):
        start = time.time()

        while self.serial.in_waiting == 0:
            if time.time() - start > self.device_timeout:
                raise TimeoutError('Device timed out.')
            time.sleep(1)

    def read_chunks(self):
        chunks = []

        start = time.time()

        while time.time() - start < self.packet_timeout:
            if self.serial.in_waiting != 0:
                chunk = self.serial.read(self.serial.in_waiting)
                chunks.append(chunk)
                start = time.time()
            time.sleep(1)

        return chunks

    def __iter__(self):
        while True:
            self.wait_for_data()
            yield b''.join(self.read_chunks())
