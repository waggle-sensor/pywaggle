# Conversion for disabled sensor notification

def convert(value):
    raw_s = value['disabled_sensor']

    sensor_id = raw_s.strip().split(',')
    value = {}
    for i in range(len(sensor_id)):
        # print(sensor_id[i], type(sensor_id[i]))
        if sensor_id[i]:
            num = 'disabled_id_' + str(i)
            value[num] = (sensor_id[i], 'disabled')

    return value
