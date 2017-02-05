from waggle.transport import TimedTransport
from waggle.coresense.utils import decode_frame
from binascii import hexlify


class CoresenseReader(object):

    def __init__(self, device):
        self.transport = TimedTransport(device,
                                        baudrate=115200,
                                        device_timeout=60,
                                        packet_timeout=5)

    def __iter__(self):
        for packet in self.transport:
            try:
                data = decode_frame(packet)
            except Exception as e:
                print('Could not decode data: data={} exc={}'.format(hexlify(packet), e))
            else:
                yield data
