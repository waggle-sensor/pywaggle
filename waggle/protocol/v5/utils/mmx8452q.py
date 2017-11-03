# Conversion for MMX8452Q accelerometer

# Metsense v 3.12 GSCALE is set to 2 (g)

def convert(value):
    GSCALE = 2
    return float(value) / float(1 << 12) / (2.0 * GSCALE), 'g'