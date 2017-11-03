# Conversion for APDS_9006_020 light sensor


def convert(value):
    # MCP output code transform factor 0.065 mV/(uW/cm^2): MCP mux
    value_voltage = value * 0.0000625
    # voltage divider factor 5/2 to calc input voltage: voltage divider circuit
    value_voltage_divider = (value_voltage * 5.00) / 2.00

    irrad = value_voltage_divider / 0.001944   # 405.1 unit: mA/lux
    return irrad, 'lux'