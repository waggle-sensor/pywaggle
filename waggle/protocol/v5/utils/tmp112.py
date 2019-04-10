# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
#
# Conversion for TMP112 temperature
#
#
# if ((Temp_byte[0] & 0x80) == 0x00)
# {
#     // it is a positive temperature
#     Temp_uint16 = Temp_byte[0];
#     Temp_uint16 = Temp_uint16 << 5;
#     Temp_uint16 = Temp_uint16 | (Temp_byte[1] >> 3);
#     Temp_float[0] = (Temp_uint16 & 0x0FFF) * 0.0625;
# }
# else
# {
#     Temp_byte[0] = ~Temp_byte[0];
#     Temp_byte[1] = ~Temp_byte[1];
#     Temp_uint16 = Temp_byte[0];
#     Temp_uint16 = Temp_uint16 << 5;
#     Temp_uint16 = Temp_uint16 | (Temp_byte[1] >> 3);
#     Temp_float[0] = (Temp_uint16 & 0x0FFF)*-0.0625;
# }

def convert(value):
    raw_t = value['metsense_tmp112']

    if (raw_t >> 15) == 0:
        # it is a positive temperature
        h = (raw_t >> 8) << 5
        l = (raw_t & 0xFF) >> 3
        temperature = (((h | l) & 0x0FFF) * 0.0625)
    else:
        h = (~(raw_t >> 8)) << 5
        l = (~(raw_t & 0xFF)) >> 3
        temperature = (((h | l) & 0x0FFF) * -0.0625)

    temperature_rounded = round(temperature, 2)
    value['metsense_tmp112'] = (temperature_rounded, 'C')

    return value
