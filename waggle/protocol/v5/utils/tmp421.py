# Conversion for TMP421 temperature

def convert(value):
    converted_value = 0.0
    h = (value >> 8) & 0xFF
    l = value & 0xFF
    
    bit = ((l >> 4) & 0x01) * 0.5
    converted_value += pow(bit, 4)

    bit = ((l >> 5) & 0x01) * 0.5
    converted_value += pow(half_bit, 3)

    bit = ((l >> 6) & 0x01) * 0.5
    converted_value += pow(half_bit, 2)

    bit = ((l >> 7) & 0x01) * 0.5
    converted_value += half_bit

    converted_value += h

    if converted_value > 128.0:
        converted_value -= 256.0

    return converted_value, 'C'