# Available formats:
# a - signed integer
# b - unsigned integer
# c - hex string
# d - time epoch
# e - float
# f: fixed point (-127.99, 127.99)
# g: fixed point (-31.999, 31.999)

# Available conversions:
# epoch_datetime - date time from time epoch
# acs764 - ACS764 current sensor on Wagman
# MF52C1103F3380 - MF52 thermistor on Wagman
# MF52C1103F3380_NC - MF52 thermistor on Wagman for nodecontroller
# HTU21D_temperature - HTU21D sensor on Wagman
# HTU21D_humidity - HTU21D sensor on Wagman
# HIH4030 - HIH4030 humidity
# photocell - photocell on Wagman
# bool - True/False mapped from 1/0
# TMP112 - TMP112 temperature sensor
# pr103j2 - PR103J2 temperature sensor
waggleprotocol_spec = '''
- id: 0xFD
  params:
    - name: metsense_ver_hw_mj
      length: 0.375
      format: b
      conversion:
    - name: metsense_ver_hw_mi
      length: 0.375
      format: b
      conversion:
    - name: metsense_ver_sw_mj
      length: 0.5
      format: b
      conversion:
    - name: metsense_ver_sw_mi
      length: 0.75
      format: b
      conversion:
    - name: metsense_build_time
      length: 4
      format: d
      conversion: epoch_datetime
    - name: metsense_build_git
      length: 2
      format: c
      conversion:

- id: 0x00
  params:
    - name: metsense_id
      length: 6
      format: c
      conversion:

- id: 0x01
  params:
    - name: metsense_tmp112
      length: 2
      format: f
      conversion: TMP112

- id: 0x02
  params:
    - name: metsense_htu21d_temperature
      length: 2
      format: b
      conversion: HTU21D_temperature
    - name: metsense_htu21d_humidity
      length: 2
      format: b
      conversion: HTU21D_humidity

- id: 0x03
  params:
    - name: metsense_hih4030_humidity
      length: 2
      format: b
      conversion: HIH4030

- id: 0x04
  params:
    - name: metsense_bmp180_temperature
      length: 4
      format: b
      conversion:
    - name: metsense_bmp180_pressure
      length: 4
      format: b
      conversion:

- id: 0x05
  params:
    - name: metsense_pr103j2_temperature
      length: 2
      format: b
      conversion: pr103j2

- id: 0x06
  params:
    - name: metsense_tsl250rd_light
      length: 2
      format: b
      conversion: tsl250rd_metsense

- id: 0x07
  params:
    - name: metsense_mma8452q_acc_x
      length: 2
      format: a
      conversion: mmx8452q
    - name: metsense_mma8452q_acc_y
      length: 2
      format: a
      conversion: mmx8452q
    - name: metsense_mma8452q_acc_z
      length: 2
      format: a
      conversion: mmx8452q
#    - name: metsense_mma8452q_vibration
#      length: 0
#      format: e
#      conversion: mmx8452q_vibration

- id: 0x08
  params:
    - name: metsense_spv1840lr5h-b
      length: 2
      format: b
      conversion: spv1840lr5h-b

- id: 0x09
  params:
    - name: metsense_tsys01_temperature
      length: 2
      format: b
      conversion: tsys01

- id: 0x0A
  params:
    - name: lightsense_hmc5883l_hx
      length: 2
      format: b
      conversion: hmc5883l
    - name: lightsense_hmc5883l_hy
      length: 2
      format: b
      conversion: hmc5883l
    - name: lightsense_hmc5883l_hz
      length: 2
      format: b
      conversion: hmc5883l

- id: 0x0B
  params:
    - name: lightsense_hih6130_temperature
      length: 2
      format: b
      conversion: hih6130_temperature
    - name: lightsense_hih6130_humidity
      length: 2
      format: b
      conversion: hih6130_humidity

- id: 0x0C
  params:
    - name: lightsense_apds_9006_020
      length: 2
      format: b
      conversion: apds_9006_020

- id: 0x0D
  params:
    - name: lightsense_tsl260
      length: 2
      format: b
      conversion: tsl260

- id: 0x0E
  params:
    - name: lightsense_tsl250
      length: 2
      format: b
      conversion: tsl250rd_lightsense

- id: 0x0F
  params:
    - name: lightsense_mlx75305
      length: 2
      format: b
      conversion: mlx75305

- id: 0x10
  params:
    - name: lightsense_ml8511
      length: 2
      format: b
      conversion: ml8511

- id: 0x11
  params:
    - name: lightsense_tmp421
      length: 2
      format: b
      conversion: tmp421

- id: 0x1D
  params:
    - name: metsense_sht25_temperature
      length: 2
      format: b
      conversion:
    - name: metsense_sht25_humidity
      length: 2
      format: b
      conversion:

- id: 0x50
  params:
    - name: wagman_id
      length: 6
      format: c
      conversion:

- id: 0x51
  params:
    - name: wagman_ver_hw_mj
      length: 0.5
      format: b
      conversion:
    - name: wagman_ver_hw_mi
      length: 0.5
      format: b
      conversion:

- id: 0x52
  params:
    - name: wagman_ver_sw_mj
      length: 1
      format: b
      conversion:
    - name: wagman_ver_sw_mi
      length: 1
      format: b
      conversion:
    - name: wagman_ver_sw_p
      length: 1
      format: b
      conversion:

- id: 0x53
  params:
    - name: wagman_ver_git
      length: 2
      format: c
      conversion:

- id: 0x54
  params:
    - name: wagman_time_compile
      length: 4
      format: d
      conversion: epoch_datetime

- id: 0x55
  params:
    - name: wagman_time_current
      length: 4
      format: d
      conversion: epoch_datetime

- id: 0x56
  params:
    - name: wagman_boot_flag
      length: 1
      format: b
      conversion:

- id: 0x57
  params:
    - name: wagman_time_lastboot
      length: 4
      format: d
      conversion: epoch_datetime

- id: 0x58
  params:
    - name: wagman_bootloader_nc_flag
      length: 1
      format: b
      conversion:

- id: 0x59
  params:
    - name: wagman_boot_count
      length: 1
      format: b
      conversion:

- id: 0x5A
  params:
    - name: wagman_current_wagman
      length: 2
      format: b
      conversion: acs764
    - name: wagman_current_nc
      length: 2
      format: b
      conversion: acs764
    - name: wagman_current_ep
      length: 2
      format: b
      conversion: acs764
    - name: wagman_current_cs
      length: 2
      format: b
      conversion: acs764
    - name: wagman_current_port4
      length: 2
      format: b
      conversion: acs764
    - name: wagman_current_port5
      length: 2
      format: b
      conversion: acs764

- id: 0x5B
  params:
    - name: wagman_temperature_ncheatsink
      length: 2
      format: b
      conversion: MF52C1103F3380_NC
    - name: wagman_temperature_epheatsink
      length: 2
      format: b
      conversion: MF52C1103F3380
    - name: wagman_temperature_battery
      length: 2
      format: b
      conversion: MF52C1103F3380
    - name: wagman_temperature_brainplate
      length: 2
      format: b
      conversion: MF52C1103F3380
    - name: wagman_temperature_powersupply
      length: 2
      format: b
      conversion: MF52C1103F3380

- id: 0x5C
  params:
    - name: wagman_htu21d_temperature
      length: 2
      format: b
      conversion: HTU21D_temperature
    - name: wagman_htu21d_humidity
      length: 2
      format: b
      conversion: HTU21D_humidity

- id: 0x5D
  params:
    - name: wagman_hih4030_humidity
      length: 2
      format: b
      conversion: HIH4030

- id: 0x5E
  params:
    - name: wagman_light
      length: 2
      format: b
      conversion: photocell

- id: 0x5F
  params:
    - name: wagman_failcount_nc
      length: 1
      format: b
      conversion:
    - name: wagman_failcount_ep
      length: 1
      format: b
      conversion:
    - name: wagman_failcount_cs
      length: 1
      format: b
      conversion:
    - name: wagman_failcount_port4
      length: 1
      format: b
      conversion:
    - name: wagman_failcount_port5
      length: 1
      format: b
      conversion:

- id: 0x60
  params:
    - name: wagman_enabled_nc
      length: 0.125
      format: b
      conversion: bool
    - name: wagman_enabled_ep
      length: 0.125
      format: b
      conversion: bool
    - name: wagman_enabled_cs
      length: 0.125
      format: b
      conversion: bool
    - name: wagman_enabled_port4
      length: 0.125
      format: b
      conversion: bool
    - name: wagman_enabled_port5
      length: 0.125
      format: b
      conversion: bool

- id: 0x61
  params:
    - name: wagman_mediaselect_sd_nc
      length: 0.125
      format: b
      conversion: bool
    - name: wagman_mediaselect_sd_ep
      length: 0.125
      format: b
      conversion: bool

- id: 0x62
  params:
    - name: wagman_heartbeat_nc
      length: 2
      format: b
      conversion:
    - name: wagman_heartbeat_ep
      length: 2
      format: b
      conversion:
    - name: wagman_heartbeat_cs
      length: 2
      format: b
      conversion:
    - name: wagman_heartbeat_port4
      length: 2
      format: b
      conversion:
    - name: wagman_heartbeat_port5
      length: 2
      format: b
      conversion:
    
- id: 0x63
  params:
    - name: wagman_lastboot_nc
      length: 4
      format: d
      conversion:
    - name: wagman_lastboot_ep
      length: 4
      format: d
      conversion:
    - name: wagman_lastboot_cs
      length: 4
      format: d
      conversion:
    - name: wagman_lastboot_port4
      length: 4
      format: d
      conversion:
    - name: wagman_lastboot_port5
      length: 4
      format: d
      conversion:

- id: 0x64
  params:
    - name: wagman_powerfaults_nc
      length: 4
      format: d
      conversion:
    - name: wagman_powerfaults_ep
      length: 4
      format: d
      conversion:
    - name: wagman_powerfaults_cs
      length: 4
      format: d
      conversion:
    - name: wagman_powerfaults_port4
      length: 4
      format: d
      conversion:
    - name: wagman_powerfaults_port5
      length: 4
      format: d
      conversion:

- id: 0x65
  params:
    - name: wagman_bootattempt_nc
      length: 1
      format: b
      conversion:
    - name: wagman_bootattempt_ep
      length: 1
      format: b
      conversion:
    - name: wagman_bootattempt_cs
      length: 1
      format: b
      conversion:
    - name: wagman_bootattempt_port4
      length: 1
      format: b
      conversion:
    - name: wagman_bootattempt_port5
      length: 1
      format: b
      conversion:
'''