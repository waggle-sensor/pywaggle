# Conversion for BMP180 temperature

# temperature = 
# int32_t X1 = (ut - (int32_t)_bmp085_coeffs.ac6) * ((int32_t)_bmp085_coeffs.ac5) >> 15;
#   int32_t X2 = ((int32_t)_bmp085_coeffs.mc << 11) / (X1+(int32_t)_bmp085_coeffs.md);
#   return X1 + X2;



def convert(value):
    # ac1 = 7191
    # ac2 = 64531
    # ac3 = 51317
    # ac4 = 34229
    # ac5 = 25803
    # ac6 = 15820
    # b1 = 6515
    # b2 = 32
    # mb = 32768
    # mc = 53750
    # md = 2331

  #   mode = 3

  #   ac1 = value[0]
  #   ac2 = value[1]
  #   ac3 = value[2]
  #   ac4 = value[3]

  #   ac6 = value[0]
  #   ac5 = value[1]
  #   mc = value[2]
  #   md = value[3]

  #   ut = (value[4] << 8) | value[5]

  #   x1 = ((ut - ac6) * ac5) >> 15
  #   x2 = (mc << 11) / (x1 + md)
  #   temperature = (x1 + x2 + 8) >> 4
  #   temperature /= 10


  # int32_t  ut = 0, up = 0, compp = 0;
  # int32_t  x1, x2, b5, b6, x3, b3, p;
  # uint32_t b4, b7;

  # /* Get the raw pressure and temperature values */
  # readRawTemperature(&ut);
  # readRawPressure(&up);

  # /* Temperature compensation */
  # b5 = computeB5(ut);

  # /* Pressure compensation */
  # b6 = b5 - 4000;
  # x1 = (_bmp085_coeffs.b2 * ((b6 * b6) >> 12)) >> 11;
  # x2 = (_bmp085_coeffs.ac2 * b6) >> 11;
  # x3 = x1 + x2;
  # b3 = (((((int32_t) _bmp085_coeffs.ac1) * 4 + x3) << _bmp085Mode) + 2) >> 2;
  # x1 = (_bmp085_coeffs.ac3 * b6) >> 13;
  # x2 = (_bmp085_coeffs.b1 * ((b6 * b6) >> 12)) >> 16;
  # x3 = ((x1 + x2) + 2) >> 2;
  # b4 = (_bmp085_coeffs.ac4 * (uint32_t) (x3 + 32768)) >> 15;
  # b7 = ((uint32_t) (up - b3) * (50000 >> _bmp085Mode));

  # if (b7 < 0x80000000)
  # {
  #   p = (b7 << 1) / b4;
  # }
  # else
  # {
  #   p = (b7 / b4) << 1;
  # }

  # x1 = (p >> 8) * (p >> 8);
  # x1 = (x1 * 3038) >> 16;
  # x2 = (-7357 * p) >> 16;
  # compp = p + ((x1 + x2 + 3791) >> 4);

  # /* Assign compensated pressure value */
  # *pressure = compp;

    return value
