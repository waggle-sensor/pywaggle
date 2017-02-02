from waggle.transport import TimedTransport
from waggle.coresense.utils import decode_frame


class CoresenseReader(object):

    def __init__(self, device):
        self.transport = TimedTransport(device,
                                        baudrate=115200,
                                        device_timeout=60,
                                        packet_timeout=5)

    def __iter__(self):
        for packet in self.transport:
            yield decode_frame(packet.strip())
