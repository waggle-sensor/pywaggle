# Available formats:
# a - signed integer
# b - unsigned integer
# c - hex string
# d - time epoch
# e - float
# f: fixed point (-127.99, 127.99)
# g: fixed point (-31.999, 31.999)

# h - string
# i - byte

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
- id: 0xFF
  conversion:
  params:
    - name: metsense_ver_hw_mj
      length: 0.375
      format: b
    - name: metsense_ver_hw_mi
      length: 0.375
      format: b
    - name: metsense_ver_sw_mj
      length: 0.5
      format: b
    - name: metsense_ver_sw_mi
      length: 0.75
      format: b
    - name: metsense_build_time
      length: 4
      format: d
    - name: metsense_build_git
      length: 2
      format: c

- id: 0x00
  conversion:
  params:
    - name: metsense_id
      length: 6
      format: c

- id: 0x01
  conversion: tmp112
  params:
    - name: metsense_tmp112
      length: 2
      format: b

- id: 0x02
  conversion: htu21d
  params:
    - name: metsense_htu21d_temperature
      length: 2
      format: b
    - name: metsense_htu21d_humidity
      length: 2
      format: b

- id: 0x03
  conversion: hih4030
  params:
    - name: metsense_hih4030_humidity
      length: 2
      format: b

- id: 0x04
  conversion: bmp180
  params:
    - name: metsense_bmp180_temperature
      length: 2
      format: b
    - name: metsense_bmp180_pressure
      length: 3
      format: b

- id: 0x05
  conversion: pr103j2
  params:
    - name: metsense_pr103j2_temperature
      length: 2
      format: b

- id: 0x06
  conversion: tsl250rdms
  params:
    - name: metsense_tsl250rd_light
      length: 2
      format: b

- id: 0x07
  conversion: mma8452q
  params:
    - name: metsense_mma8452q_acc_x
      length: 2
      format: b
    - name: metsense_mma8452q_acc_y
      length: 2
      format: b
    - name: metsense_mma8452q_acc_z
      length: 2
      format: b
#    - name: metsense_mma8452q_vibration
#      length: 0
#      format: e

- id: 0x08
  conversion: spv1840lr5h-b
  params:
    - name: metsense_spv1840lr5h-b
      length: 2
      format: b

- id: 0x09
  conversion: tsys01
  params:
    - name: metsense_tsys01_temperature
      length: 3
      format: b

- id: 0x0A
  conversion: hmc5883l
  params:
    - name: lightsense_hmc5883l_hx
      length: 2
      format: a
    - name: lightsense_hmc5883l_hz
      length: 2
      format: a
    - name: lightsense_hmc5883l_hy
      length: 2
      format: a

- id: 0x0B
  conversion: hih6130
  params:
    - name: lightsense_hih6130_humidity
      length: 2
      format: b
    - name: lightsense_hih6130_temperature
      length: 2
      format: b

- id: 0x0C
  conversion: apds_9006_020
  params:
    - name: lightsense_apds_9006_020_light
      length: 2
      format: b

- id: 0x0D
  conversion: tsl260
  params:
    - name: lightsense_tsl260_light
      length: 2
      format: b

- id: 0x0E
  conversion: tsl250rdls
  params:
    - name: lightsense_tsl250_light
      length: 2
      format: b

- id: 0x0F
  conversion: mlx75305
  params:
    - name: lightsense_mlx75305
      length: 2
      format: b

- id: 0x10
  conversion: ml8511
  params:
    - name: lightsense_ml8511
      length: 2
      format: b

- id: 0x13
  conversion: tmp421
  params:
    - name: lightsense_tmp421
      length: 2
      format: b

# - id: 0x1D
#   conversion: 
#   params:
#     - name: metsense_sht25_temperature
#       length: 2
#       format: b
#     - name: metsense_sht25_humidity
#       length: 2
#       format: b

- id: 0x16
  conversion: chemsense_config
  params:
    - name: chemsense_config
      length: 1514
      format: i

- id: 0x2A
  conversion: chemsense
  params:
    - name: chemsense_raw
      length: 59
      format: h

- id: 0x2B
  conversion: alpha_status
  params:
    - name: alpha_status
      length: 1
      format: a

- id: 0x28
  conversion: alpha_histo
  params:
    - name: alpha_histo
      length: 62
      format: i

- id: 0x29
  conversion: alpha_raw
  params:
    - name: alpha_serial
      length: 20
      format: h

- id: 0x30
  conversion: alpha_raw
  params:
    - name: alpha_firmware
      length: 2
      format: i

- id: 0x31
  conversion: alpha_config
  params:
    - name: alpha_config
      length: 128
      format: i

- id: 0x50
  conversion: 
  params:
    - name: wagman_id
      length: 6
      format: c

- id: 0x51
  conversion: 
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
  conversion: 
  params:
    - name: wagman_ver_sw_mj
      length: 1
      format: b
    - name: wagman_ver_sw_mi
      length: 1
      format: b
    - name: wagman_ver_sw_p
      length: 1
      format: b

- id: 0x53
  conversion: 
  params:
    - name: wagman_ver_git
      length: 2
      format: c

- id: 0x54
  conversion: epoch_datetime
  params:
    - name: wagman_time_compile
      length: 4
      format: d

- id: 0x55
  conversion: epoch_datetime
  params:
    - name: wagman_time_current
      length: 4
      format: d

- id: 0x56
  conversion: 
  params:
    - name: wagman_boot_flag
      length: 1
      format: b

- id: 0x57
  conversion: epoch_datetime
  params:
    - name: wagman_time_lastboot
      length: 4
      format: d

- id: 0x58
  conversion: 
  params:
    - name: wagman_bootloader_nc_flag
      length: 1
      format: b

- id: 0x59
  conversion: 
  params:
    - name: wagman_boot_count
      length: 1
      format: b

- id: 0x5A
  conversion: acs764
  params:
    - name: wagman_current_wagman
      length: 2
      format: b
    - name: wagman_current_nc
      length: 2
      format: b
    - name: wagman_current_ep
      length: 2
      format: b
    - name: wagman_current_cs
      length: 2
      format: b
    - name: wagman_current_port4
      length: 2
      format: b
    - name: wagman_current_port5
      length: 2
      format: b

- id: 0x5B
  conversion: mf52c1103f3380
  params:
    - name: wagman_temperature_ncheatsink
      length: 2
      format: b
    - name: wagman_temperature_epheatsink
      length: 2
      format: b
    - name: wagman_temperature_battery
      length: 2
      format: b
    - name: wagman_temperature_brainplate
      length: 2
      format: b
    - name: wagman_temperature_powersupply
      length: 2
      format: b

- id: 0x5C
  conversion: htu21d
  params:
    - name: wagman_htu21d_temperature
      length: 2
      format: b
    - name: wagman_htu21d_humidity
      length: 2
      format: b

- id: 0x5D
  conversion: hih4030
  params:
    - name: wagman_hih4030_humidity
      length: 2
      format: b

- id: 0x5E
  conversion: photocell
  params:
    - name: wagman_light
      length: 2
      format: b

- id: 0x5F
  conversion: 
  params:
    - name: wagman_failcount_nc
      length: 1
      format: b
    - name: wagman_failcount_ep
      length: 1
      format: b
    - name: wagman_failcount_cs
      length: 1
      format: b
    - name: wagman_failcount_port4
      length: 1
      format: b
    - name: wagman_failcount_port5
      length: 1
      format: b

- id: 0x60
  conversion: bool
  params:
    - name: wagman_enabled_nc
      length: 0.125
      format: b
    - name: wagman_enabled_ep
      length: 0.125
      format: b
    - name: wagman_enabled_cs
      length: 0.125
      format: b
    - name: wagman_enabled_port4
      length: 0.125
      format: b
    - name: wagman_enabled_port5
      length: 0.125
      format: b

- id: 0x61
  conversion: bool
  params:
    - name: wagman_mediaselect_sd_nc
      length: 0.125
      format: b
    - name: wagman_mediaselect_sd_ep
      length: 0.125
      format: b

- id: 0x62
  conversion: 
  params:
    - name: wagman_heartbeat_nc
      length: 2
      format: b
    - name: wagman_heartbeat_ep
      length: 2
      format: b
    - name: wagman_heartbeat_cs
      length: 2
      format: b
    - name: wagman_heartbeat_port4
      length: 2
      format: b
    - name: wagman_heartbeat_port5
      length: 2
      format: b
    
- id: 0x63
  conversion: 
  params:
    - name: wagman_lastboot_nc
      length: 4
      format: d
    - name: wagman_lastboot_ep
      length: 4
      format: d
    - name: wagman_lastboot_cs
      length: 4
      format: d
    - name: wagman_lastboot_port4
      length: 4
      format: d
    - name: wagman_lastboot_port5
      length: 4
      format: d

- id: 0x64
  conversion: 
  params:
    - name: wagman_powerfaults_nc
      length: 4
      format: d
    - name: wagman_powerfaults_ep
      length: 4
      format: d
    - name: wagman_powerfaults_cs
      length: 4
      format: d
    - name: wagman_powerfaults_port4
      length: 4
      format: d
    - name: wagman_powerfaults_port5
      length: 4
      format: d

- id: 0x65
  conversion: 
  params:
    - name: wagman_bootattempt_nc
      length: 1
      format: b
    - name: wagman_bootattempt_ep
      length: 1
      format: b
    - name: wagman_bootattempt_cs
      length: 1
      format: b
    - name: wagman_bootattempt_port4
      length: 1
      format: b
    - name: wagman_bootattempt_port5
      length: 1
      format: b
'''