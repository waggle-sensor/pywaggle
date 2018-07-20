from .protocol import pack_sensorgrams
from .protocol import pack_datagrams
from .protocol import pack_waggle_packets
from .protocol import unpack_sensorgrams
from .protocol import unpack_datagrams
from .protocol import unpack_waggle_packets


def pack_message(message):
    return pack_waggle_packets([message])


def unpack_message(data):
    return unpack_waggle_packets(data)[0]


def pack_datagram(datagram):
    return pack_datagrams([datagram])


def unpack_datagram(data):
    return unpack_datagrams(data)[0]


def pack_sensorgram(sensorgram):
    return pack_sensorgrams([sensorgram])


def unpack_sensorgram(data):
    return unpack_sensorgrams(data)[0]


def pack_sensor_data_message(sensorgrams):
    if isinstance(sensorgrams, list):
        data = pack_sensorgrams(sensorgrams)
    elif isinstance(sensorgrams, bytes) or isinstance(sensorgrams, bytearray):
        data = sensorgrams
    else:
        raise ValueError('Invalid sensorgram type. Must be list or bytes.')

    return pack_message({
        'receiver_id': '0000000000000000',
        'receiver_sub_id': '0000000000000000',
        'body': pack_datagram({
            'body': data
        })
    })
