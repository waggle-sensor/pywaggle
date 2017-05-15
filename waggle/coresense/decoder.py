from binascii import unhexlify
from format import unpack
from packet import decode_packet
import yaml
from pprint import pprint
import logging

logger = logging.getLogger('coresense.decoder')


def identity(x):
    return x


def tmp112(x):
    return 2*x - 1


def htu21d_humidty(x):
    return 100 * x


with open('spec.yml') as f:
    sensors = yaml.load(f.read())


formatnames = {
    'macaddr': 3,
}


for sensor in sensors:
    sensor['name'] = sensor['name'].lower()

    # translate format names
    for param in sensor['params']:
        if isinstance(param['format'], str):
            param['format'] = formatnames[param['format']]

    sensor['format'] = ''.join(str(param['format']) for param in sensor['params'])

    for param in sensor['params']:
        param['calc'] = globals()[param.get('calc', 'identity')]


sensors_by_id = dict((sensor['id'], sensor) for sensor in sensors)


def main():
    packet = decode_packet(unhexlify('aa30cbfd886442584838a594b2008600001814bcf301821838038200c90485183c0142cc05820350068202d1078800018101000001010882033b098218540a86818d809982840b842a0c184e0c8200420d8253cf0e8257d00f827af5108225581382251f20860004a3e2a1fd1d8409a3027b1e8509420144251f8602131e626d3415830000131a8300969e1c83859cc919830073b31883059cc817830006b81b8300123f218209542282097e238209b9248209f725820a1f2689800a03e100140000002789000300018001000000a655'))

    for subpacket in packet['subpackets']:
        if subpacket['id'] not in sensors_by_id:
            logger.warn('unknown subpacket id {}'.format(subpacket['id']))
            continue

        sensor = sensors_by_id[subpacket['id']]

        subpacket['name'] = sensor['name']

        try:
            values = unpack(sensor['format'], subpacket['body'])
        except AssertionError:
            continue

        subpacket['params'] = []

        for param, value in zip(sensor['params'], values):
            subpacket['params'].append({
                'name': param['name'],
                'unit': param['unit'],
                'raw': value,
                'value': param['calc'](value),
            })

    pprint(packet)


if __name__ == '__main__':
    main()
