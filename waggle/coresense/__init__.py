# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import re


def parse_sensor_table(text):
    spec = {}

    for chunk in re.split('\n\n+', text.strip()):
        lines = chunk.splitlines()

        sensor_id = int(lines[0].strip(), 16)
        sensor_name = lines[1].strip()
        fields = [tuple(map(str.strip, line.split(':'))) for line in lines[2:]]

        fmts = ''.join(fmt.strip() for _, fmt in fields)
        keys = [key.strip().lower() for key, _ in fields]

        spec[sensor_id] = (sensor_name, fmts, keys)

    return spec


spec = parse_sensor_table('''
00
Coresense ID
mac_address : 3

01
TMP112
temperature : 6

02
HTU21D
temperature : 6
humidity : 6

03
HIH4030
humidity : 1

04
BMP180
temperature : 6
pressure : 4

05
PR103J2
temperature : 1

06
TSL250RD-AS
intensity : 1

07
MMA8452Q
acceleration.x : 6
acceleration.y : 6
acceleration.z : 6
rms : 6

08
SPV1840LR5H-B
intensity : 1

09
TSYS01
temperature : 6

0A
HMC5883L
magnetic_field.x : 8
magnetic_field.y : 8
magnetic_field.z : 8

0B
HIH6130
temperature : 6
humidity : 6

0C
APDS-9006-020
intensity : 1

0D
TSL260RD
intensity : 1

0E
TSL250RD-LS
intensity : 1

0F
MLX75305
intensity : 1

10
ML8511
intensity : 1

11
D6T
temperatures : ?

12
MLX90614
temperature : 6

13
TMP421
temperature : 6

14
SPV1840LR5H-B
intensity : ?

15
Chemsense
reducing_gases : 5

16
Chemsense
ethanol : 5

17
Chemsense
no2 : 5

18
Chemsense
o3 : 5

19
Chemsense
h2s : 5

1A
Chemsense
oxidizing_gases : 5

1B
Chemsense
co : 5

1C
Chemsense
so2 : 5

1D
SHT25
temperature : 2
humidity : 2

1E
LPS25H
temperature : 2
pressure : 4

1F
Si1145
ir_intensity : 1
uv_intensity : 1
visible_light_intensity : 1

20
Chemsense ID
mac_address : 3

21
CO ADC Temp
adc_temperature : 2

22
IAQ/IRR Temp
adc_temperature : 2

23
O3/NO2 Temp
adc_temperature : 2

24
SO2/H2S Temp
adc_temperature : 2

25
CO LMP Temp
adc_temperature : 2

26
BMI160
acceleration.x : 2
acceleration.y : 2
acceleration.z : 2
index : 4

27
BMI160
orientation.x : 2
orientation.y : 2
orientation.z : 2
index : 4

FC
Rain Gauge
tip_count : 1

FB
Soil Moisture
dielectric : 6
conductivity : 6
temperature : 6
''')
