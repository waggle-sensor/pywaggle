# Conversion for TSL250RD in Metsense

def convert(value):
    value_voltage = (value * 3.3) / 1024.0
    
    # a = (math.log10(0.04)-math.log10(0.6))/(math.log10(0.6)-1)
    # b = math.log10(3)/(a*math.log10(50))
    # irrad = 10**((math.log10(input) - b)/a)

    irrad = value_voltage / 0.064
    return irrad, 'uW/cm^2'