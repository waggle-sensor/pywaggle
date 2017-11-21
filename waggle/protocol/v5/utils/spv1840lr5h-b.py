# Conversion for SPV1840LR5H-B

# V_I = (SPV_TSL_RAW - 1.75) / 453.33 - 1.75   # raw voltage of SPV
# SPV_RAW = (-V_I * 1023.00) / 5.00          # raw integer [0, 1023] of SPV

import math

def convert(value):
    raw_s = value['metsense_spv1840lr5h-b']

    # def convert_to_db(value):
    #     value_voltage = value * 5.0 / 1024.0
    #     raw = value_voltage / 453.3333 - 1.65
    #     return math.log10(-raw)*-20
    #     # return math.log10(raw) * 20.0

    # reading = []
    # for i in range(1, len(raw_s), 2):
    #     value = (raw_s[i - 1] << 8) | raw_s[i]
    #     reading.append(convert_to_db(value))

    # value['metsense_spv1840lr5h-b'] = (sum(reading)/len(reading), 'dB')


    value['metsense_spv1840lr5h-b'] = (round(sum(raw_s)/len(raw_s), 2), 'dB')

    return value