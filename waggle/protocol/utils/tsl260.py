# Conversion for TSL260 light sensor

def convert(value):
    # MCP output code transform factor 0.065 mV/(uW/cm^2): MCP mux
    value_voltage = value * 0.0000625
    # voltage divider factor 5/2 to calc input voltage: voltage divider circuit
    value_voltage_divider = (value_voltage * 5.00) / 2.00

    # input unit: V, irrad unit: uW/cm^2
    irrad = (value_voltage_divider - 0.006250) / 0.058
    return irrad, 'uW/cm^2'