# Conversion for HIH4030 at 5 V

# At 25 C the best linear fit is
# y = x * 30.68 (mV/%RH) + 0.958 V

def convert(value):
    v = float(value) / 1024.0 * 5.0
    humidity = v * 30.68 + 0.958
    return round(humidity, 2), '%RH'