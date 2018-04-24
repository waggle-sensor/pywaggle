## Change logs

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
* format of PMS7003's header is changed from `hex` to `byte` to fix decode error

* Fixed parameter names of PMS7003, NC/EP services, NC/EP ipaddress, NC/EP git repos, Wagman mediaselect/powerfault

* Chemsense.py converter temporally outputs raw data instead of converted data

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