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


def encode_bytes(b):
    return b


def encode_uint(size, x):
    return x.to_bytes(size, 'big')


def encode_int(size, x):
    return x.to_bytes(size, 'big', signed=True)


def encode_sensorgram(sg):
    body = sg['value']

    return b''.join([
        encode_uint(2, len(body)),
        encode_uint(4, sg.get('timestamp') or nows()),
        encode_uint(2, sg['id']),
        encode_uint(1, sg.get('inst', 0)),
        encode_uint(1, sg['subid']),
        encode_uint(2, sg.get('sourceid', 0)),
        encode_uint(1, sg.get('sourceinst', 0)),
        encode_bytes(body),
    ])


DATAGRAM_HEADER = bytes([0xaa])
DATAGRAM_FOOTER = bytes([0x55])
DATAGRAM_PROTOCOL_VERSION = 1


def encode_datagram(dg):
    body = dg['body']

    return b''.join([
        encode_bytes(DATAGRAM_HEADER),
        encode_uint(3, len(body)),
        encode_uint(1, DATAGRAM_PROTOCOL_VERSION),
        encode_uint(4, dg.get('timestamp') or nows()),
        encode_uint(2, dg.get('packet_seq') or 0),
        encode_uint(1, dg.get('packet_type') or 0),
        encode_uint(2, dg['plugin_id']),
        encode_uint(1, dg['plugin_version'][0]),
        encode_uint(1, dg['plugin_version'][1]),
        encode_uint(1, dg['plugin_version'][2]),
        encode_uint(1, dg.get('plugin_instance') or 0),
        encode_uint(2, dg.get('plugin_run_id') or 0),
        encode_bytes(body),
        encode_uint(1, calccrc8(body)),
        encode_bytes(DATAGRAM_FOOTER),
    ])


def encode_waggle_packet(p):
    header = b''.join([
        encode_uint(1, p.get('protocol_major_version') or 0),
        encode_uint(1, p.get('protocol_minor_version') or 0),
        encode_uint(1, p.get('protocol_patch_version') or 0),
        encode_uint(1, p.get('message_priority') or 0),
        encode_uint(4, p.get('body_length') or 0),
        encode_uint(4, p.get('timestamp') or nows()),
        encode_uint(1, p.get('message_major_type') or 0),
        encode_uint(1, p.get('message_minor_type') or 0),
        encode_uint(2, p.get('reserved') or 0),
        encode_bytes(p.get('sender_id') or b'0000000000000000'),
        encode_bytes(p.get('sender_sub_id') or b'0000000000000000'),
        encode_bytes(p.get('receiver_id') or b'0000000000000000'),
        encode_bytes(p.get('receiver_sub_id') or b'0000000000000000'),
        encode_uint(3, p.get('sender_seq') or 0),
        encode_uint(2, p.get('sender_sid') or 0),
        encode_uint(3, p.get('response_seq') or 0),
        encode_uint(2, p.get('response_sid') or 0),
    ])

    return b''.join([
        header,
        encode_uint(2, crc16(header)),
        encode_uint(4, p.get('token') or 0),
        encode_bytes(p['body']),
        encode_uint(4, crc32(p['body'])),
    ])


def decode_bytes(size, b):
    return b[:size], b[size:]


def decode_uint(size, b):
    chunk, b = decode_bytes(size, b)
    return int.from_bytes(chunk, 'big'), b


def decode_sensorgram(b):
    bodysize, b = decode_uint(2, b)
    timestamp, b = decode_uint(4, b)
    id, b = decode_uint(2, b)
    inst, b = decode_uint(1, b)
    subid, b = decode_uint(1, b)
    sourceid, b = decode_uint(2, b)
    sourceinst, b = decode_uint(1, b)
    body, b = decode_bytes(bodysize, b)

    return {
        'timestamp': timestamp,
        'id': id,
        'inst': inst,
        'subid': subid,
        'sourceid': sourceid,
        'sourceinst': sourceinst,
        'body': body,
    }, b


def decode_datagram(b):
    try:
        start = b.index(DATAGRAM_HEADER)
    except ValueError:
        return None, b''

    bstart = b[start:]
    b = bstart

    _, b = decode_bytes(len(DATAGRAM_HEADER), b)
    bodysize, b = decode_uint(3, b)
    protocol_version, b = decode_uint(1, b)
    timestamp, b = decode_uint(4, b)
    packet_seq, b = decode_uint(2, b)
    packet_type, b = decode_uint(1, b)
    plugin_id, b = decode_uint(2, b)
    plugin_major_version, b = decode_uint(1, b)
    plugin_minor_version, b = decode_uint(1, b)
    plugin_patch_version, b = decode_uint(1, b)
    plugin_instance, b = decode_uint(1, b)
    plugin_run_id, b = decode_uint(2, b)
    body, b = decode_bytes(bodysize, b)
    crc, b = decode_uint(1, b)
    footer, b = decode_bytes(len(DATAGRAM_FOOTER), b)

    if footer != DATAGRAM_FOOTER:
        return None, bstart

    if crc != calccrc8(body):
        return None, bstart

    return {
        'protocol_version': protocol_version,
        'timestamp': timestamp,
        'plugin_id': plugin_id,
        'plugin_instance': plugin_instance,
        'plugin_run_id': plugin_run_id,
        'packet_seq': packet_seq,
        'packet_type': packet_type,
        'plugin_version': (plugin_major_version, plugin_minor_version, plugin_patch_version),
        'body': body,
    }, b


def encode_multiple(xs, f):
    return b''.join([f(x) for x in xs])


def encode_sensorgrams(sensorgrams):
    return encode_multiple(sensorgrams, encode_sensorgram)


def encode_datagrams(datagrams):
    return encode_multiple(datagrams, encode_datagram)


def decode_multiple(b, f):
    while True:
        if not b:
            return

        x, b = f(b)

        if x is None:
            return

        yield x


def decode_sensorgrams(b):
    return decode_multiple(b, decode_sensorgram)


def decode_datagrams(b):
    return decode_multiple(b, decode_datagram)


if __name__ == '__main__':
    print(encode_waggle_packet({
        'body': b'testing!'
    }))

    packed = encode_datagram({
        'plugin_id': 1000,
        'plugin_version': (1, 0, 0),
        'body': encode_sensorgrams([
            {'id': 1, 'subid': 20, 'value': b'xxx'},
            {'id': 1, 'subid': 20, 'value': b'abc'},
            {'id': 1, 'subid': 20, 'value': b'123'},
        ])
    })

    packed = b''.join([packed] * 2)

    for dg in decode_datagrams(packed[:-2]):
        print('datagram')
        print(dg)
