# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import binascii


#=======================
#    Helper functions
#=======================


def get_key_value(str_data):
    sp = str_data.strip().split(' ')
    if len(sp) == 2:
        return sp[0], sp[1]
    else:
        return None, None


def find_sensor_id_from_param_name(spec, param_name):
    for sensor_id in spec:
        sensor_record = spec[sensor_id]
        sensor_params = sensor_record['params']
        for param in sensor_params:
            if param_name == param['name']:
                return sensor_id
    return None


def find_param_names_and_types_of_sensor(spec, sensor_id):
    if sensor_id not in spec:
        return None
    sensor = spec[sensor_id]
    sensor_params = sensor['params']
    ret_name = []
    ret_type = []
    for param in sensor_params:
        ret_name.append(param['name'])
        ret_type.append(param['format'])
    return ret_name, ret_type


def try_converting(value, value_type):
    try:
        if 'int' in value_type:
            return int(value)
        elif 'float' in value_type:
            return float(value)
        elif 'epoch' in value_type:
            return int(value)
        elif 'byte' in value_type:
            if isinstance(value, bytes):
                value = value.decode()
            return binascii.unhexlify(value)
        else:
            return value
    except Exception:
        return None
