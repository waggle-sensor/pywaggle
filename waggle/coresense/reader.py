# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
from waggle.transport import TimedTransport
from waggle.coresense.utils import decode_frame
from binascii import hexlify
import sys


class CoresenseReader(object):

    def __init__(self, device):
        self.transport = TimedTransport(device,
                                        baudrate=115200,
                                        device_timeout=60,
                                        packet_timeout=5)

    def __iter__(self):
        for packet in self.transport:
            try:
                start = packet.index(0xAA)
                end = packet.rindex(0x55) + 1

                assert start < end

                if start != 0 and end != len(packet):
                    print('WARN unexpected packet padding: {}'.format(hexlify(packet)), file=sys.stderr)

                data = decode_frame(packet[start:end])
            except Exception as exc:
                print('ERROR could not decode packet: {} <{}>'.format(hexlify(packet), exc), file=sys.stderr)
            else:
                yield data
