# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import logging
from .spec import spec
from . import format
from .helper import get_key_value, find_sensor_id_from_param_name, find_param_names_and_types_of_sensor, try_converting
import waggle.checksum

logger = logging.getLogger('protocol.encoder')

# protocol_version 1 is used in lower or equal to coresense firmware 3.12
protocol_version = 2


def encode_sub_packet(id, data=[]):
    '''
    Encode a sub packet
    @params:
        id - ID of the sub packet
        data - A list of parameters for the ID
    @return:
        A binary type sub packet
        None when failed
    '''

    try:
        params = spec[id]['params']
    except KeyError:
        logger.error('ID %d is unknown' % (id,))
        return None

    if not isinstance(data, list):
        logger.error('%s must be a list' % (str(data),))
        return None

    if len(params) != len(data):
        logger.error('Length of the %s must be matched' % (str(data),))
        return None

    formats = [param['format'] for param in params]
    lengths = [param['length'] for param in params]
    binary = format.waggle_pack(formats, lengths, data)

    packet_length = len(binary)
    sub_packet = bytearray(2)
    sub_packet[0] = id
    sub_packet[1] = 0x80 | packet_length
    sub_packet.extend(binary)

    return sub_packet


def encode_frame(frame_data):
    '''
    Encode a frame
    @params:
        - dict {sensorid: values, ...}
    @return:
        A byte array of the frame
    '''
    if not isinstance(frame_data, dict):
        logger.error('%s must be a dictionary' % (str(frame_data),))
        return None

    bodies = []
    body = bytearray()
    max_body_length = 2**8 - 1
    for sub_id in frame_data:
        assert isinstance(sub_id, int)

        sub_values = frame_data[sub_id]
        encoded = encode_sub_packet(sub_id, sub_values)

        if encoded is not None:
            if len(body) + len(encoded) >= max_body_length:
                bodies.append(body)
                body = bytearray()
            body.extend(encoded)

    bodies.append(body)

    waggle_packet = bytearray()
    packet_type = 0  # sensor reading
    for index, body in enumerate(bodies):
        body_length = len(body)

        header = bytearray(3)
        header[0] = 0xAA
        header[1] = ((packet_type & 0x0F) << 4) | protocol_version & 0x0F
        header[2] = body_length + 1

        # Sequence
        packet_body = bytearray(1)
        if index + 1 == len(bodies):
            packet_body[0] = index | 0x80
        else:
            packet_body[0] = index
        packet_body.extend(body)

        footer = bytearray(2)
        footer[0] = waggle.checksum.crc8(packet_body)
        footer[1] = 0x55

        waggle_packet.extend(header)
        waggle_packet.extend(packet_body)
        waggle_packet.extend(footer)

    return bytes(waggle_packet)


def encode_frame_from_flat_string(frame_data, verbose=False):
    '''
    Encode a frame
    @params:
        - lines of string 'nc_machine_id 1234...\nnc_boot_id 123....'
    @return:
        A byte array of the frame
    '''

    if not isinstance(frame_data, str):
        print('Input must be string. Abort.')
        return None

    keys = []
    values = []
    list_of_inputs = frame_data.splitlines()
    for line in list_of_inputs:
        if not line.strip():
            continue

        key, value = get_key_value(line)
        if key is not None and value is not None:
            keys.append(key)
            values.append(value)
        else:
            if verbose:
                print('Could not parse %s' % (line,))

    dict_data = {}
    number_of_keys = len(keys)
    for i in range(0, number_of_keys):
        key = keys[i]
        if key == '':
            continue
        value = values[i]

        # Check if sensor ID for the key exists
        sensor_id = find_sensor_id_from_param_name(spec, key)
        if sensor_id is None:
            if verbose:
                print('Sensor ID not exist for %s' % (key,))
            continue

        # Check if all required params exists in the list of inputs
        required_params, required_types = find_param_names_and_types_of_sensor(spec, sensor_id)
        required_values = [None] * len(required_params)
        for j in range(i, number_of_keys):
            key_in_search = keys[j]

            if key_in_search in required_params:
                index = required_params.index(key_in_search)
                value_in_search = values[j]
                conversion_type = required_types[index]
                # Convert the value into proper type
                converted_value_in_search = try_converting(value_in_search, conversion_type)
                if converted_value_in_search is not None:
                    required_values[index] = converted_value_in_search
                else:
                    if verbose:
                        print('%s is not type of %s' % (value_in_search, conversion_type))
                    continue
                # Prevent the key from being called later
                keys[j] = ''
        if None in required_values:
            if verbose:
                print('Not all params exists for %s' % (str(sensor_id),))
            continue

        dict_data[sensor_id] = required_values
    return encode_frame(dict_data)
