# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for PMS7003 particle sensor

def convert(value):
    header = value['pms7003_header']
    length = value['pms7003_frame_length']
    pm1_cf1 = value['pms7003_pm1_cf1']
    pm25_cf1 = value['pms7003_pm25_cf1']
    pm10_cf1 = value['pms7003_pm10_cf1']
    pm1_atm = value['pms7003_pm1_atm']
    pm25_atm = value['pms7003_pm25_atm']
    pm10_atm = value['pms7003_pm10_atm']
    p3particle = value['pms7003_point_3um_particle']
    p5particle = value['pms7003_point_5um_particle']
    p1particle = value['pms7003_1um_particle']
    p25particle = value['pms7003_2_5um_particle']
    p5particle = value['pms7003_5um_particle']
    p10particle = value['pms7003_10um_particle']
    ver = value['pms7003_version']
    ec = value['pms7003_error_code']
    cs = value['pms7003_check_sum']

    value['pms7003_header'] = (header, '')
    value['pms7003_frame_length'] = (length, '')
    value['pms7003_pm1_cf1'] = (pm1_cf1, 'ug/m3')
    value['pms7003_pm25_cf1'] = (pm25_cf1, 'ug/m3')
    value['pms7003_pm10_cf1'] = (pm10_cf1, 'ug/m3')
    value['pms7003_pm1_atm'] = (pm1_atm, 'ug/m3')
    value['pms7003_pm25_atm'] = (pm25_atm, 'ug/m3')
    value['pms7003_pm10_atm'] = (pm10_atm, 'ug/m3')
    value['pms7003_point_3um_particle'] = (p3particle, 'particles')
    value['pms7003_point_5um_particle'] = (p5particle, 'particles')
    value['pms7003_1um_particle'] = (p1particle, 'particles')
    value['pms7003_2_5um_particle'] = (p25particle, 'particles')
    value['pms7003_5um_particle'] = (p5particle, 'particles')
    value['pms7003_10um_particle'] = (p10particle, 'particles')
    value['pms7003_version'] = (ver, '')
    value['pms7003_error_code'] = (ec, '')
    value['pms7003_check_sum'] = (cs, '')

    return value
