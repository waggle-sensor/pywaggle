from .protocol import pack_sensorgrams
from .protocol import pack_datagrams
from .protocol import pack_waggle_packets
from .protocol import unpack_sensorgrams
from .protocol import unpack_datagrams
from .protocol import unpack_waggle_packets


def pack_sensor_message(sensorgrams):
    return pack_waggle_packets([
        {
            'receiver_id': '0000000000000000',
            'receiver_sub_id': '0000000000000000',
            'body': pack_datagrams([
                {
                    'body': pack_sensorgrams(sensorgrams),
                }
            ])
        }
    ])


def pack_comm_message(message):
    return pack_waggle_packets([
        {
            'receiver_id': message['receiver_id'],
            'receiver_sub_id': message['receiver_sub_id'],
            'body': pack_datagrams([
                {
                    'body': message['body'],
                }
            ])
        }
    ])


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
