# Conversion for TMP112 temperature

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
    if (value >> 15) & 0x01 == 0:
        pass
    else:
        pass
    return value, 'C'