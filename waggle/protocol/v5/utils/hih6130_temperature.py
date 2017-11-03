# Conversion for HIH6130 temperature

# temperature value (x - do not care)
# bbbbbbbb bbbbbbxx
# y (C) = x / (2^14-1) * 165 - 40
# -40 C = 0 counts
# 125 C = 2^14 - 1 counts

def convert(value):
    shifted_value = (value >> 2) & 0x3FFF
    converted_value = float(shifted_value) * 1.0071415e-2 - 40.0
    return converted_value, 'C'
