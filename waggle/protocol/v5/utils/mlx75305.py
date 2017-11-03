# Conversion for MLX75305 light sense

def convert(value):
    # MCP output code transform factor 0.065 mV/(uW/cm^2): MCP mux
    value_voltage = value * 0.0000625
    # voltage divider factor 5/2 to calc input voltage: voltage divider circuit
    value_voltage_divider = (value_voltage * 5.00) / 2.00

    converted_value = (value_voltage_divider - 0.09234) / 0.007   #with gain 1, the factor is 7mA/(uW/cm^2)
    return converted_value, 'uW/cm^2'