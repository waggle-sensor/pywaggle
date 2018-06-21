import time
import io
from waggle.checksum import crc8


def pack_uint(n, x):
    if n == 1:
        return bytes([x & 0xff])
    if n == 2:
        return bytes([(x >> 8) & 0xff, x & 0xff])
    if n == 3:
        return bytes([(x >> 16) & 0xff, (x >> 8) & 0xff, x & 0xff])
    if n == 4:
        return bytes([(x >> 24) & 0xff, (x >> 16) & 0xff, (x >> 8) & 0xff, x & 0xff])
    raise ValueError('Invalid integer size.')


def unpack_uint(n, b):
    if n == 1:
        return b[0]
    if n == 2:
        return (b[0] << 8) | b[1]
    if n == 3:
        return (b[0] << 16) | (b[1] << 8) | b[2]
    if n == 4:
        return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]
    raise ValueError('Invalid integer size.')


def write_uint(w, n, x):
    w.write(pack_uint(n, x))


def read_uint(r, n):
    return unpack_uint(n, r.read(n))


def get_timestamp_or_now(obj):
    if 'timestamp' in obj:
        return obj['timestamp']
    return int(time.time())


def write_sensorgram(w, sensorgram):
    write_uint(w, 2, len(sensorgram['body']))
    write_uint(w, 2, sensorgram['sensor_id'])
    write_uint(w, 1, sensorgram.get('sensor_instance', 0))
    write_uint(w, 1, sensorgram['parameter_id'])
    write_uint(w, 4, get_timestamp_or_now(sensorgram))
    w.write(sensorgram['body'])


def read_sensorgram(r):
    body_length = read_uint(r, 2)

    return {
        'sensor_id': read_uint(r, 2),
        'sensor_instance': read_uint(r, 1),
        'parameter_id': read_uint(r, 1),
        'timestamp': read_uint(r, 4),
        'body': r.read(body_length),
    }


def write_datagram(w, datagram):
    write_uint(w, 1, 0xaa)
    write_uint(w, 3, len(datagram['body']))
    write_uint(w, 1, datagram.get('protocol_version', 2))
    write_uint(w, 4, get_timestamp_or_now(datagram))
    write_uint(w, 2, datagram.get('packet_seq', 0))
    write_uint(w, 1, datagram.get('packet_type', 0))
    write_uint(w, 2, datagram['plugin_id'])
    write_uint(w, 1, datagram['plugin_major_version'])
    write_uint(w, 1, datagram['plugin_minor_version'])
    write_uint(w, 1, datagram['plugin_patch_version'])
    write_uint(w, 1, datagram['plugin_instance'])
    write_uint(w, 2, datagram['plugin_run_id'])
    w.write(datagram['body'])
    write_uint(w, 1, crc8(datagram['body']))
    write_uint(w, 1, 0x55)


def read_datagram(r):
    assert read_uint(r, 1) == 0xaa
    body_length = read_uint(r, 3)

    datagram = {
        'protocol_version': read_uint(r, 1),
        'timestamp': read_uint(r, 4),
        'packet_seq': read_uint(r, 2),
        'packet_type': read_uint(r, 1),
        'plugin_id': read_uint(r, 2),
        'plugin_major_version': read_uint(r, 1),
        'plugin_minor_version': read_uint(r, 1),
        'plugin_patch_version': read_uint(r, 1),
        'plugin_instance': read_uint(r, 1),
        'plugin_run_id': read_uint(r, 2),
        'body': r.read(body_length),
    }

    assert read_uint(r, 1) == crc8(datagram['body'])
    assert read_uint(r, 1) == 0x55

    return datagram

# Header(64B)
# 0-7	[Protocol Maj Ver (1B)][Protocol Min Ver (1B)][Build Version (1B)][Msg Priority (1B)][Length of Message Body (4B)]
# 8-15	[Time (4B)][Msg Maj Type (1B)][Msg Min Type (1B)][Reserved (2B)]
# 16-23   [Sender Node ID {7:0}(8B)]
# 24-31   [Sender Subsystem ID {7:0}(8B)]
# 32-39	[Receiver Node ID {7:0}(8B)]
# 40-47	[Receiver Subsystem ID {7:0}(8B)]
# 46-55 	[Sender Seq No. (3B)] [Sender Session ID (2B)] [Responding to Seq No. (3B)]
# 56-63 	[Responding to Session ID (2B)][CRC (2B)][Token (4B)]
#
# [Payload / Body]
#
# [CRC_32  (4B)]


if __name__ == '__main__':
    w = io.BytesIO()

    write_sensorgram(w, {
        'sensor_id': 1,
        'parameter_id': 0,
        'body': b'12345',
    })

    write_sensorgram(w, {
        'sensor_id': 2,
        'parameter_id': 1,
        'body': b'abc',
    })

    write_sensorgram(w, {
        'sensor_id': 3,
        'parameter_id': 4,
        'sensor_instance': 3,
        'timestamp': 777,
        'body': b'xyz',
    })

    r = io.BytesIO(w.getvalue())

    print(read_sensorgram(r))
    print(read_sensorgram(r))
    print(read_sensorgram(r))

    datagram = {
        'plugin_id': 1,
        'plugin_major_version': 4,
        'plugin_minor_version': 0,
        'plugin_patch_version': 1,
        'plugin_instance': 0,
        'plugin_run_id': 0,
        'body': w.getvalue(),
    }

    w = io.BytesIO()

    write_datagram(w, datagram)

    r = io.BytesIO(w.getvalue())
    print(read_datagram(r))
