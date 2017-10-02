# Conversion for HIH6130 humidity

# humidity value
# ssbbbbbb bbbbbbbb (s - status bit)
# 0 %RH = 0 counts
# 100 %RH = 2^14 - 1 counts

# humidity = raw_value / (2^14 - 1) * 100

def convert(value):
    masked_value = value & 0x3FFF
    humidity = float(masked) * 6.103888e-3
    return humidity, '%RH'