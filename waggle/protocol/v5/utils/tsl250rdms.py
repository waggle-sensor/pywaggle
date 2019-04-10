# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
# Conversion for TSL250RD in Metsense

def convert(value):
    raw_l = value['metsense_tsl250rd_light']

    value_voltage = (raw_l * 3.3) / 1024.0

    # a = (math.log10(0.04)-math.log10(0.6))/(math.log10(0.6)-1)
    # b = math.log10(3)/(a*math.log10(50))
    # irrad = 10**((math.log10(input) - b)/a)

    irrad = value_voltage / 0.064

    irrad_rounded = round(irrad, 3)
    value['metsense_tsl250rd_light'] = (irrad_rounded, 'uW/cm^2')
    # value['metsense_tsl250rd_light'] = (raw_l, 'raw')

    return value
