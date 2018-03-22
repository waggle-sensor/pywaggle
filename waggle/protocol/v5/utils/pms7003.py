# Conversion for PMS7003 particle sensor

def convert(value):
    header = value['header']
    length = value['frame_length']
    pm1_cf1 = value['pm1_cf1']
    pm25_cf1 = value['pm25_cf1']
    pm10_cf1 = value['pm10_cf1']
    pm1_atm = value['pm1_atm']
    pm25_atm = value['pm25_atm']
    pm10_atm = value['pm10_atm']
    p3particle = value['point_3um_particle'] 
    p5particle = value['point_5um_particle']
    p1particle = value['1um_particle']
    p25particle = value['2_5um_particle']
    p5particle = value['5um_particle']
    p10particle = value['10um_particle']
    ver = value['version']
    ec = value['error_code']
    cs = value['check_sum']

    value['header'] = (header, '')
    value['frame_length'] = (length, '')
    value['pm1_cf1'] = (pm1_cf1, 'ug/m3')
    value['pm25_cf1'] = (pm25_cf1, 'ug/m3')
    value['pm10_cf1'] = (pm10_cf1, 'ug/m3')
    value['pm1_atm'] = (pm1_atm, 'ug/m3')
    value['pm25_atm'] = (pm25_atm, 'ug/m3')
    value['pm10_atm'] = (pm10_atm, 'ug/m3')
    value['point_3um_particle'] = (p3particle, 'particles')
    value['point_5um_particle'] = (p5particle, 'particles')
    value['1um_particle'] = (p1particle, 'particles')
    value['2_5um_particle'] = (p25particle, 'particles')
    value['5um_particle'] = (p5particle, 'particles')
    value['10um_particle'] = (p10particle, 'particles')
    value['version'] = (ver, '')
    value['error_code'] = (ec, '')
    value['check_sum'] = (cs, '')

    return value
