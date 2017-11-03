# Conversion for SPV1840LR5H-B

# V_I = (SPV_TSL_RAW - 1.75) / 453.33 - 1.75   # raw voltage of SPV
# SPV_RAW = (-V_I * 1023.00) / 5.00          # raw integer [0, 1023] of SPV

import math

def convert(value):
    value_voltage = value * 5.0 / 1024.0
    raw = value_voltage / 453.3333 - 1.65
    db = math.log10(raw) * 20.0
    return db, 'dB'