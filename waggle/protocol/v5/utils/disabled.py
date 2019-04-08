# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for disabled sensor notification

def convert(value):
    raw_s = value['disabled_sensor']

    sensor_id = raw_s.strip().split(b'\xab')

    value = {}

    for i in range(len(sensor_id)):
        # print(sensor_id[i], type(sensor_id[i]))
        if sensor_id[i]:
            num = 'disabled_id_' + str(i)
            value[num] = (sensor_id[i][0], 'disabled')

    return value
