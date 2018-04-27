## Change logs

### 0.23.10 (2018-04-27)
#### New features
* `disabled_sensor_list` with sensor ID `0x32` is added

This is to serve disabled sensor list coming from Metsense firmware. With this change, `disabled_sensor` that uses sensor ID `0x12` is deprecated

#### Refactoring
* Alphasense (OPC-N2) conversion is cleaned up and its decoding is checked by checksum
* Pipeline/RMQHandler will attempt to reconnect if publishing a message failed on `send` function

* Precisions for sensors are reconfigured:
    - 1 decimal point precision sensors: BMP180 temperature (sensor id: 0x04)
    - 2 decimal point precision sensors: TMP112, HTU21D temperature and pressure, HIH4030, BMP180 pressure, PR103j2, SPV1840, TSYS01, HIH6130 temperature and humidity, TMP421, and all Chemsense data (sensor id: 0x01, 0x02, 0x03, 0x04, 0x05, 0x08, 0x09, 0x0B, 0x13, and 0x15 - 0x27)
    - 3 decimal point precision sensors: TSL250_MS MMA8452, HMC5883, APDS, TSL260, TSL250_LS, MLX75305, ML8511, and pm values from Alpha sensor  (sensor id: 0x06, 0x07, 0x0A, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, and some parts of 0x28)

### 0.23.9 (2018-04-25)
#### New features

* Added Wagman HTU21D parameters.
* Added new sensor: disabled sensor list, sensor id is 0x32. (2018-04-27)
* Modified parameter name of disabled sensor, which is for sensor id 0x12: automatically sent by FW when a user request any sensor data. (2018-04-27)

#### Refactoring

* Extracted optimized, shared checksum function into `waggle/checksum.py`.
* PR103J2 uses standard library bisect for binary search.

### 0.23.8 (2018-04-10)
#### New features

* Added many status service parameters.
* Added `audio_spl` parameters.
* Added image processing parameters (avg color, histogram).

#### Fixes

* Fixed MF52C1103f3380 converter variable names - was mixing `v_in` and `Vin`.

### 0.23.7 (2018-04-06)
#### New features
* `encode_frame_from_flat_string`

Encoding packets from string type input
```
data = 'wagman_ver_git 1ef3'
print(encode_frame_from_flat_string(data))
b'\xaa\x02\x05\x80S\x82\x1e\xf3\x10U'
```

#### Fixes
* Format of PMS7003's header is changed from `hex` to `byte` to fix decode error

* Fixed parameter names of PMS7003, NC/EP services, NC/EP ipaddress, NC/EP git repos, Wagman mediaselect/powerfault. For example, prefixed PMS7003 parameters with `pms7003_`.

* Chemsense converter reverted to output raw data instead of converted data. (Intended to be hold over fix.)

### 0.23.6 (2018-04-04)
#### New features
* `net_usb` is added

### 0.23.5 (2018-03-30)
#### New features
* `net_broadband` and `net_lan` sensors are added

### 0.23.4 (2018-03-22)
#### New features
* Chemsense conversion using calibration data

* PMS7003 (a.k.a plantower) is added to the specification

#### Fixes
* Waggle spec format

Formats are more human readable. For example, format `a` is changed to `uint`, `b` to `int`, and such

### 0.23.3 (2018-02-14)

* Added chemsense calibration data.
* Added support for "disabled" sensor.
* Updated `spv1840lr5h-b` conversion.

### 0.23.2 (2018-01-26)

* Added support for variable length formats.
* Updated `spv1840lr5h-b` conversion.
* Renamed formats to more user friendly names. For example, `e` vs `float`.
* Added initial status sensor entries in spec.

### 0.23.1 (2018-01-16)

* Cleanup + refactoring chemsense converter.
* Prefixed alphasense parameters with `alphasense_`
* Added support for flagging sensor subpackets marked invalid.
