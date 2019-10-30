from binascii import crc_hqx
from binascii import crc32
from datetime import datetime

CRC8_TABLE = [
    0x00, 0x5e, 0xbc, 0xe2, 0x61, 0x3f, 0xdd, 0x83,
    0xc2, 0x9c, 0x7e, 0x20, 0xa3, 0xfd, 0x1f, 0x41,
    0x9d, 0xc3, 0x21, 0x7f, 0xfc, 0xa2, 0x40, 0x1e,
    0x5f, 0x01, 0xe3, 0xbd, 0x3e, 0x60, 0x82, 0xdc,
    0x23, 0x7d, 0x9f, 0xc1, 0x42, 0x1c, 0xfe, 0xa0,
    0xe1, 0xbf, 0x5d, 0x03, 0x80, 0xde, 0x3c, 0x62,
    0xbe, 0xe0, 0x02, 0x5c, 0xdf, 0x81, 0x63, 0x3d,
    0x7c, 0x22, 0xc0, 0x9e, 0x1d, 0x43, 0xa1, 0xff,
    0x46, 0x18, 0xfa, 0xa4, 0x27, 0x79, 0x9b, 0xc5,
    0x84, 0xda, 0x38, 0x66, 0xe5, 0xbb, 0x59, 0x07,
    0xdb, 0x85, 0x67, 0x39, 0xba, 0xe4, 0x06, 0x58,
    0x19, 0x47, 0xa5, 0xfb, 0x78, 0x26, 0xc4, 0x9a,
    0x65, 0x3b, 0xd9, 0x87, 0x04, 0x5a, 0xb8, 0xe6,
    0xa7, 0xf9, 0x1b, 0x45, 0xc6, 0x98, 0x7a, 0x24,
    0xf8, 0xa6, 0x44, 0x1a, 0x99, 0xc7, 0x25, 0x7b,
    0x3a, 0x64, 0x86, 0xd8, 0x5b, 0x05, 0xe7, 0xb9,
    0x8c, 0xd2, 0x30, 0x6e, 0xed, 0xb3, 0x51, 0x0f,
    0x4e, 0x10, 0xf2, 0xac, 0x2f, 0x71, 0x93, 0xcd,
    0x11, 0x4f, 0xad, 0xf3, 0x70, 0x2e, 0xcc, 0x92,
    0xd3, 0x8d, 0x6f, 0x31, 0xb2, 0xec, 0x0e, 0x50,
    0xaf, 0xf1, 0x13, 0x4d, 0xce, 0x90, 0x72, 0x2c,
    0x6d, 0x33, 0xd1, 0x8f, 0x0c, 0x52, 0xb0, 0xee,
    0x32, 0x6c, 0x8e, 0xd0, 0x53, 0x0d, 0xef, 0xb1,
    0xf0, 0xae, 0x4c, 0x12, 0x91, 0xcf, 0x2d, 0x73,
    0xca, 0x94, 0x76, 0x28, 0xab, 0xf5, 0x17, 0x49,
    0x08, 0x56, 0xb4, 0xea, 0x69, 0x37, 0xd5, 0x8b,
    0x57, 0x09, 0xeb, 0xb5, 0x36, 0x68, 0x8a, 0xd4,
    0x95, 0xcb, 0x29, 0x77, 0xf4, 0xaa, 0x48, 0x16,
    0xe9, 0xb7, 0x55, 0x0b, 0x88, 0xd6, 0x34, 0x6a,
    0x2b, 0x75, 0x97, 0xc9, 0x4a, 0x14, 0xf6, 0xa8,
    0x74, 0x2a, 0xc8, 0x96, 0x15, 0x4b, 0xa9, 0xf7,
    0xb6, 0xe8, 0x0a, 0x54, 0xd7, 0x89, 0x6b, 0x35,
]


def calccrc8(data, crc=0):
    """Computes CRC of data using CRC8 with 0x8c polynomial."""
    for value in data:
        crc = CRC8_TABLE[crc ^ value]
    return crc


def crc16(data):
    return crc_hqx(data, 0)


def nows():
    return int(datetime.utcnow().timestamp())


DATAGRAM_HEADER = bytes([0xaa])
DATAGRAM_FOOTER = bytes([0x55])
DATAGRAM_PROTOCOL_VERSION = 1


class Encoder:

    def __init__(self):
        self.blocks = []

    def encoded_bytes(self):
        return b''.join(self.blocks)

    def bytes(self, b):
        self.blocks.append(b)
        return self

    def uint(self, size, x):
        self.bytes(x.to_bytes(size, 'big'))
        return self

    def int(self, size, x):
        self.bytes(x.to_bytes(size, 'big', signed=True))
        return self

    def tuple2(self, t):
        self.uint(1, t[0])
        self.uint(1, t[1])
        return self

    def tuple3(self, t):
        self.uint(1, t[0])
        self.uint(1, t[1])
        self.uint(1, t[2])
        return self

    def sensorgram(self, sg):
        body = sg['value']
        self.uint(2, len(body))
        self.uint(4, sg.get('timestamp') or nows())
        self.uint(2, sg['id'])
        self.uint(1, sg.get('inst', 0))
        self.uint(1, sg['subid'])
        self.uint(2, sg.get('sourceid', 0))
        self.uint(1, sg.get('sourceinst', 0))
        self.bytes(body)
        return self

    def datagram(self, dg):
        body = dg['body']
        self.bytes(DATAGRAM_HEADER)
        self.uint(3, len(body))
        self.uint(1, DATAGRAM_PROTOCOL_VERSION)
        self.uint(4, dg.get('timestamp') or nows())
        self.uint(2, dg.get('packet_seq') or 0)
        self.uint(1, dg.get('packet_type') or 0)
        self.uint(2, dg['plugin_id'])
        self.tuple3(dg['plugin_version'])
        self.uint(1, dg.get('plugin_instance') or 0)
        self.uint(2, dg.get('plugin_run_id') or 0)
        self.bytes(body)
        self.uint(1, calccrc8(body))
        self.bytes(DATAGRAM_FOOTER)
        return self

    def ident(self, b):
        if len(b) != 8:
            raise ValueError(b)
        return self.bytes(b)

    def packet_header(self, p, bodysize):
        self.tuple3(p.get('protocol_version') or (0, 0, 0))
        self.uint(1, p.get('message_priority') or 0)
        self.uint(4, bodysize)
        self.uint(4, p.get('timestamp') or nows())
        self.tuple2(p.get('message_type') or (0, 0))
        self.uint(2, p.get('reserved') or 0)
        self.ident(p.get('sender_id') or b'00000000')
        self.ident(p.get('sender_sub_id') or b'00000000')
        self.ident(p.get('receiver_id') or b'00000000')
        self.ident(p.get('receiver_sub_id') or b'00000000')
        self.uint(3, p.get('sender_seq') or 0)
        self.uint(2, p.get('sender_sid') or 0)
        self.uint(3, p.get('response_seq') or 0)
        self.uint(2, p.get('response_sid') or 0)
        return self

    def packet(self, p):
        body = p['body']
        bodysize = len(body)

        header = Encoder().packet_header(p, bodysize).encoded_bytes()

        self.bytes(header)
        self.uint(2, crc16(header))
        self.uint(4, p.get('token') or 0)
        self.bytes(body)
        self.uint(4, crc32(body))
        return self


class Decoder:

    def __init__(self, buf):
        self.buf = buf

    def bytes(self, size):
        r = self.buf[:size]

        if len(r) != size:
            raise EOFError()

        self.buf = self.buf[size:]
        return r

    def uint(self, size):
        return int.from_bytes(self.bytes(size), 'big')

    def int(self, size):
        return int.from_bytes(self.bytes(size), 'big', signed=True)

    def tuple2(self):
        t0 = self.uint(1)
        t1 = self.uint(1)
        return (t0, t1)

    def tuple3(self):
        t0 = self.uint(1)
        t1 = self.uint(1)
        t2 = self.uint(1)
        return (t0, t1, t2)

    def sensorgram(self):
        bodysize = self.uint(2)

        return {
            'timestamp': self.uint(4),
            'id': self.uint(2),
            'inst': self.uint(1),
            'subid': self.uint(1),
            'sourceid': self.uint(2),
            'sourceinst': self.uint(1),
            'value': self.bytes(bodysize),
        }

    def datagram(self):
        r = {}

        try:
            start = self.buf.index(DATAGRAM_HEADER)
            self.buf = self.buf[start:]
        except ValueError:
            self.buf = b''
            return None

        self.bytes(len(DATAGRAM_HEADER))
        bodysize = self.uint(3)
        r['protocol_version'] = self.uint(1)
        r['timestamp'] = self.uint(4)
        r['packet_seq'] = self.uint(2)
        r['packet_type'] = self.uint(1)
        r['plugin_id'] = self.uint(2)
        r['plugin_version'] = self.tuple3()
        r['plugin_instance'] = self.uint(1)
        r['plugin_run_id'] = self.uint(2)
        r['body'] = self.bytes(bodysize)
        crc = self.uint(1)
        footer = self.bytes(len(DATAGRAM_FOOTER))

        if footer != DATAGRAM_FOOTER:
            return None

        if crc != calccrc8(r['body']):
            return None

        return r

    def ident(self):
        return self.bytes(8)

    def packet_header(self):
        headersize = 3+1+4+4+2+2+8+8+8+8+3+2+3+2
        crcCalc = crc16(self.buf[:headersize])

        r = {}

        r['protocol_version'] = self.tuple3()
        r['message_priority'] = self.uint(1)
        bodysize = self.uint(4)
        r['timestamp'] = self.uint(4)
        r['message_type'] = self.tuple2()
        r['reserved'] = self.uint(2)
        r['sender_id'] = self.bytes(8)
        r['sender_sub_id'] = self.bytes(8)
        r['receiver_id'] = self.bytes(8)
        r['receiver_sub_id'] = self.bytes(8)
        r['sender_seq'] = self.uint(3)
        r['sender_sid'] = self.uint(2)
        r['response_seq'] = self.uint(3)
        r['response_sid'] = self.uint(2)
        crc = self.uint(2)

        if crc != crcCalc:
            raise ValueError(
                'Packet header CRC invalid. {} != {}'.format(crc, crcCalc))

        return r, bodysize

    def packet(self):
        r, bodysize = self.packet_header()
        r['token'] = self.uint(4)

        crcCalc = crc32(self.buf[:bodysize])

        r['body'] = self.bytes(bodysize)
        crc = self.uint(4)

        if crc != crcCalc:
            raise ValueError(
                'Packet body CRC invalid. {} != {}'.format(crc, crcCalc))

        return r

    def sensorgrams(self):
        while self.buf:
            yield self.sensorgram()

    def datagrams(self):
        while self.buf:
            yield self.datagram()

    def packets(self):
        while self.buf:
            yield self.packet()


def encode_sensorgram(x):
    return Encoder().sensorgram(x).encoded_bytes()


def encode_datagram(x):
    return Encoder().datagram(x).encoded_bytes()


def encode_packet(x):
    return Encoder().packet(x).encoded_bytes()


def decode_sensorgram(buf):
    return Decoder(buf).sensorgram()


def decode_sensorgrams(buf):
    return Decoder(buf).sensorgrams()


def decode_datagram(buf):
    return Decoder(buf).datagram()


def decode_datagrams(buf):
    return Decoder(buf).datagrams()


def decode_packet(buf):
    return Decoder(buf).packet()


def test_invert(encode, decode, before):
    after = decode(encode(before))
    for k in before.keys():
        assert before[k] == after[k]
    print('ok')


if __name__ == '__main__':
    test_invert(encode_sensorgram, decode_sensorgram, {
        'id': 1,
        'subid': 1,
        'value': b'testing',
    })

    test_invert(encode_datagram, decode_datagram, {
        'plugin_id': 1,
        'plugin_version': (1, 2, 3),
        'body': b'testing',
    })

    test_invert(encode_packet, decode_packet, {
        'timestamp': 1,
        'body': b'testing',
    })
