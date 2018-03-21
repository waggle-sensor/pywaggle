# Available formats:
# int - signed integer
# uint - unsigned integer
# hex - hex string
# epoch - time epoch
# float - float
# float_2: fixed point (-127.99, 127.99)
# float_3: fixed point (-31.999, 31.999)

# str - string
# byte - byte

# Available conversions:
# epoch_datetime - date time from time epoch
# acs764 - ACS764 current sensor on Wagman
# MF52C1103F3380 - MF52 thermistor on Wagman
# HTU21D_temperature - HTU21D sensor on Wagman
# HTU21D_humidity - HTU21D sensor on Wagman
# HIH4030 - HIH4030 humidity
# photocell - photocell on Wagman
# bool - True/False mapped from 1/0
# TMP112 - TMP112 temperature sensor
# pr103j2 - PR103J2 temperature sensor
waggleprotocol_spec = '''
- id: 0x11
  conversion: busreading
  params:
    - name: bus_reading
      length:
      format: byte

- id: 0x12
  conversion: disabled
  params:
    - name: disabled_sensor
      length: 2
      format: hex

- id: 0xFF
  conversion:
  params:
    - name: metsense_ver_hw_mj
      length: 0.375
      format: uint
    - name: metsense_ver_hw_mi
      length: 0.375
      format: uint
    - name: metsense_ver_sw_mj
      length: 0.5
      format: uint
    - name: metsense_ver_sw_mi
      length: 0.75
      format: uint
    - name: metsense_build_time
      length: 4
      format: epoch
    - name: metsense_build_git
      length: 2
      format: hex

- id: 0x00
  conversion:
  params:
    - name: metsense_id
      length: 6
      format: hex

- id: 0x01
  conversion: tmp112
  params:
    - name: metsense_tmp112
      length: 2
      format: uint

- id: 0x02
  conversion: htu21d
  params:
    - name: metsense_htu21d_temperature
      length: 2
      format: uint
    - name: metsense_htu21d_humidity
      length: 2
      format: uint

- id: 0x03
  conversion: hih4030
  params:
    - name: metsense_hih4030_humidity
      length: 2
      format: uint

- id: 0x04
  conversion: bmp180
  params:
    - name: metsense_bmp180_temperature
      length: 2
      format: uint
    - name: metsense_bmp180_pressure
      length: 3
      format: uint

- id: 0x05
  conversion: pr103j2
  params:
    - name: metsense_pr103j2_temperature
      length: 2
      format: uint

- id: 0x06
  conversion: tsl250rdms
  params:
    - name: metsense_tsl250rd_light
      length: 2
      format: uint

- id: 0x07
  conversion: mma8452q
  params:
    - name: metsense_mma8452q_acc_x
      length: 2
      format: uint
    - name: metsense_mma8452q_acc_y
      length: 2
      format: uint
    - name: metsense_mma8452q_acc_z
      length: 2
      format: uint

- id: 0x08
  conversion: spv1840lr5h-b
  params:
    - name: metsense_spv1840lr5h-b
      length: 126
      format: byte

- id: 0x09
  conversion: tsys01
  params:
    - name: metsense_tsys01_temperature
      length: 3
      format: uint

- id: 0x0A
  conversion: hmc5883l
  params:
    - name: lightsense_hmc5883l_hx
      length: 2
      format: int
    - name: lightsense_hmc5883l_hz
      length: 2
      format: int
    - name: lightsense_hmc5883l_hy
      length: 2
      format: int

- id: 0x0B
  conversion: hih6130
  params:
    - name: lightsense_hih6130_humidity
      length: 2
      format: uint
    - name: lightsense_hih6130_temperature
      length: 2
      format: uint

- id: 0x0C
  conversion: apds_9006_020
  params:
    - name: lightsense_apds_9006_020_light
      length: 2
      format: uint

- id: 0x0D
  conversion: tsl260
  params:
    - name: lightsense_tsl260_light
      length: 2
      format: uint

- id: 0x0E
  conversion: tsl250rdls
  params:
    - name: lightsense_tsl250_light
      length: 2
      format: uint

- id: 0x0F
  conversion: mlx75305
  params:
    - name: lightsense_mlx75305
      length: 2
      format: uint

- id: 0x10
  conversion: ml8511
  params:
    - name: lightsense_ml8511
      length: 2
      format: uint

- id: 0x13
  conversion: tmp421
  params:
    - name: lightsense_tmp421
      length: 2
      format: uint

- id: 0x16
  conversion: chemsense_config
  params:
    - name: chemsense_config
      length: 1514
      format: byte

- id: 0x2A
  conversion: chemsense
  params:
    - name: chemsense_raw
      length:
      format: str

- id: 0x2B
  conversion: alpha_status
  params:
    - name: alpha_status
      length: 1
      format: int

- id: 0x2C
  conversion: onset_rain
  params:
    - name: onset_rain
      length: 1
      format: uint

- id: 0x2D
  conversion: decagon_soil
  params:
    - name: dielectric
      length: 2
      format: int
    - name: volumatric_water_content
      length: 2
      format: int
    - name: temperature
      length: 2
      format: int

- id: 0x28
  conversion: alpha_histo
  params:
    - name: alpha_histo
      length: 62
      format: byte

- id: 0x29
  conversion: alpha_raw
  params:
    - name: alpha_serial
      length: 20
      format: str

- id: 0x30
  conversion: alpha_raw
  params:
    - name: alpha_firmware
      length: 2
      format: byte

- id: 0x31
  conversion: alpha_config
  params:
    - name: alpha_config
      length: 128
      format: byte

- id: 0x36
  conversion: pms7003
  params:
    - name: pms7003_particle
      length: 32
      format: hex

- id: 0x50
  conversion:
  params:
    - name: wagman_id
      length: 6
      format: hex

- id: 0x51
  conversion:
  params:
    - name: wagman_ver_hw_mj
      length: 0.5
      format: uint
      conversion:
    - name: wagman_ver_hw_mi
      length: 0.5
      format: uint
      conversion:

- id: 0x52
  conversion:
  params:
    - name: wagman_ver_sw_mj
      length: 1
      format: uint
    - name: wagman_ver_sw_mi
      length: 1
      format: uint
    - name: wagman_ver_sw_p
      length: 1
      format: uint

- id: 0x53
  conversion:
  params:
    - name: wagman_ver_git
      length: 2
      format: hex

- id: 0x54
  conversion: epoch_datetime
  params:
    - name: wagman_time_compile
      length: 4
      format: epoch

- id: 0x55
  conversion: epoch_datetime
  params:
    - name: wagman_time_current
      length: 4
      format: epoch

- id: 0x56
  conversion:
  params:
    - name: wagman_boot_flag
      length: 1
      format: uint

- id: 0x57
  conversion: epoch_datetime
  params:
    - name: wagman_uptime
      length: 4
      format: epoch

- id: 0x58
  conversion:
  params:
    - name: wagman_bootloader_nc_flag
      length: 1
      format: uint

- id: 0x59
  conversion:
  params:
    - name: wagman_boot_count
      length: 1
      format: uint

- id: 0x5A
  conversion: acs764
  params:
    - name: wagman_current_wagman
      length: 2
      format: uint
    - name: wagman_current_nc
      length: 2
      format: uint
    - name: wagman_current_ep
      length: 2
      format: uint
    - name: wagman_current_cs
      length: 2
      format: uint
    - name: wagman_current_port4
      length: 2
      format: uint
    - name: wagman_current_port5
      length: 2
      format: uint

- id: 0x5B
  conversion: mf52c1103f3380
  params:
    - name: wagman_temperature_ncheatsink
      length: 2
      format: uint
    - name: wagman_temperature_epheatsink
      length: 2
      format: uint
    - name: wagman_temperature_battery
      length: 2
      format: uint
    - name: wagman_temperature_brainplate
      length: 2
      format: uint
    - name: wagman_temperature_powersupply
      length: 2
      format: uint

- id: 0x5C
  conversion: htu21d
  params:
    - name: wagman_htu21d_temperature
      length: 2
      format: uint
    - name: wagman_htu21d_humidity
      length: 2
      format: uint

- id: 0x5D
  conversion: hih4030
  params:
    - name: wagman_hih4030_humidity
      length: 2
      format: uint

- id: 0x5E
  conversion: photocell
  params:
    - name: wagman_light
      length: 2
      format: uint

- id: 0x5F
  conversion:
  params:
    - name: wagman_failcount_nc
      length: 1
      format: uint
    - name: wagman_failcount_ep
      length: 1
      format: uint
    - name: wagman_failcount_cs
      length: 1
      format: uint
    - name: wagman_failcount_port4
      length: 1
      format: uint
    - name: wagman_failcount_port5
      length: 1
      format: uint

- id: 0x60
  conversion: bool
  params:
    - name: wagman_enabled_nc
      length: 0.125
      format: uint
    - name: wagman_enabled_ep
      length: 0.125
      format: uint
    - name: wagman_enabled_cs
      length: 0.125
      format: uint
    - name: wagman_enabled_port4
      length: 0.125
      format: uint
    - name: wagman_enabled_port5
      length: 0.125
      format: uint

- id: 0x61
  conversion: bool
  params:
    - name: wagman_mediaselect_sd_nc
      length: 0.125
      format: uint
    - name: wagman_mediaselect_sd_ep
      length: 0.125
      format: uint

- id: 0x62
  conversion:
  params:
    - name: wagman_heartbeat_nc
      length: 4
      format: uint
    - name: wagman_heartbeat_ep
      length: 4
      format: uint
    - name: wagman_heartbeat_cs
      length: 4
      format: uint
    - name: wagman_heartbeat_port4
      length: 4
      format: uint
    - name: wagman_heartbeat_port5
      length: 4
      format: uint

- id: 0x63
  conversion:
  params:
    - name: wagman_lastboot_nc
      length: 4
      format: epoch
    - name: wagman_lastboot_ep
      length: 4
      format: epoch
    - name: wagman_lastboot_cs
      length: 4
      format: epoch
    - name: wagman_lastboot_port4
      length: 4
      format: epoch
    - name: wagman_lastboot_port5
      length: 4
      format: epoch

- id: 0x64
  conversion:
  params:
    - name: wagman_powerfaults_nc
      length: 4
      format: epoch
    - name: wagman_powerfaults_ep
      length: 4
      format: epoch
    - name: wagman_powerfaults_cs
      length: 4
      format: epoch
    - name: wagman_powerfaults_port4
      length: 4
      format: epoch
    - name: wagman_powerfaults_port5
      length: 4
      format: epoch

- id: 0x65
  conversion:
  params:
    - name: wagman_bootattempt_nc
      length: 1
      format: uint
    - name: wagman_bootattempt_ep
      length: 1
      format: uint
    - name: wagman_bootattempt_cs
      length: 1
      format: uint
    - name: wagman_bootattempt_port4
      length: 1
      format: uint
    - name: wagman_bootattempt_port5
      length: 1
      format: uint

- id: 0x66
  conversion: epoch_datetime
  params:
    - name: wagman_rtc
      length: 4
      format: uint

- id: 0x70
  conversion:
  params:
    - name: nc_node_id
      length: 12
      format: hex

- id: 0x71
  conversion:
  params:
    - name: nc_boot_id
      length: 32
      format: hex

- id: 0x72
  conversion:
  params:
    - name: nc_cpu_temp
      length: 2
      format: float_2

- id: 0x73
  conversion:
  params:
    - name: nc_ram_total
      length: 2
      format: float_2
    - name: nc_ram_free
      length: 2
      format: float_2

- id: 0x74
  conversion:
  params:
    - name: nc_current_disk_name
      length: 7
      format: str
    - name: nc_current_disk_type
      length: 2
      format: str
    - name: nc_alternate_disk_name
      length: 7
      format: str
    - name: nc_alternate_disk_type
      length: 2
      format: str
    - name: nc_partition1_total
      length: 2
      format: float_2
    - name: nc_partition1_used
      length: 1
      format: uint
    - name: nc_partition2_total
      length: 2
      format: float_2
    - name: nc_partition2_used
      length: 1
      format: uint
    - name: nc_partition3_total
      length: 2
      format: float_2
    - name: nc_partition3_used
      length: 1
      format: uint

- id: 0x75
  conversion:
  params:
    - name: nc_current_time
      length: 4
      format: epoch

- id: 0x76
  conversion:
  params:
    - name: nc_uptime
      length: 4
      format: uint
    - name: nc_idletime
      length: 4
      format: uint

- id: 0x77
  conversion:
  params:
    - name: nc_load_1
      length: 2
      format: float_2
    - name: nc_load_5
      length: 2
      format: float_2
    - name: nc_load_10
      length: 2
      format: float_2

- id: 0x78
  conversion:
  params:
    - name: nc_ipaddress
      length: 15
      format: str

- id: 0x79
  conversion:
  params:
    - name: nc_hbmode
      length: 6
      format: str

- id: 0x7A
  conversion:
  params:
    - name: nc_lock_fs
      length: 0.125
      format: uint
    - name: nc_lock_pw
      length: 0.125
      format: uint

- id: 0x7B
  conversion:
  params:
    - name: nc_beehive_ping
      length: 0.125
      format: uint
    - name: nc_beehive_sshd
      length: 0.125
      format: uint
    - name: nc_local_sshd
      length: 0.125
      format: uint

- id: 0x7C
  conversion:
  params:
    - name: nc_devices_alphasense
      length: 0.125
      format: uint
    - name: nc_devices_metsense
      length: 0.125
      format: uint
    - name: nc_devices_modem
      length: 0.125
      format: uint
    - name: nc_devices_wagman
      length: 0.125
      format: uint

- id: 0x7D
  conversion:
  params:
    - name: nc_ver_core_mj
      length: 1
      format: uint
    - name: nc_ver_core_mi
      length: 1
      format: uint
    - name: nc_ver_core_p
      length: 1
      format: uint
    - name: nc_ver_nodecontroller_mj
      length: 1
      format: uint
    - name: nc_ver_nodecontroller_mi
      length: 1
      format: uint
    - name: nc_ver_nodecontroller_p
      length: 1
      format: uint
    - name: nc_ver_pluginmanager_mj
      length: 1
      format: uint
    - name: nc_ver_pluginmanager_mi
      length: 1
      format: uint
    - name: nc_ver_pluginmanager_p
      length: 1
      format: uint

- id: 0x7E
  conversion:
  params:
    - name: nc_rabbitmq_queues_data
      length: 0.125
      format: uint
    - name: nc_rabbitmq_exchages_data
      length: 0.125
      format: uint
    - name: nc_rabbitmq_shovels_data
      length: 0.125
      format: uint
    - name: nc_rabbitmq_shovels_images
      length: 0.125
      format: uint

- id: 0x7F
  conversion:
  params:
    - name: nc_service_rabbitmq_uptime
      length: 4
      format: epoch
    - name: nc_service_rabbitmq_exitcode
      length: 1
      format: uint
    - name: nc_service_rabbitmq_state
      length: 0.5
      format: uint
    - name: nc_service_rabbitmq_substate
      length: 0.5
      format: uint
    - name: nc_service_init_uptime
      length: 4
      format: epoch
    - name: nc_service_init_exitcode
      length: 1
      format: uint
    - name: nc_service_init_state
      length: 0.5
      format: uint
    - name: nc_service_init_substate
      length: 0.5
      format: uint
    - name: nc_service_heartbeat_uptime
      length: 4
      format: epoch
    - name: nc_service_heartbeat_exitcode
      length: 1
      format: uint
    - name: nc_service_heartbeat_state
      length: 0.5
      format: uint
    - name: nc_service_heartbeat_substate
      length: 0.5
      format: uint
    - name: nc_service_epoch_uptime
      length: 4
      format: epoch
    - name: nc_service_epoch_exitcode
      length: 1
      format: uint
    - name: nc_service_epoch_state
      length: 0.5
      format: uint
    - name: nc_service_epoch_substate
      length: 0.5
      format: uint
    - name: nc_service_reversetunnel_uptime
      length: 4
      format: epoch
    - name: nc_service_reversetunnel_exitcode
      length: 1
      format: uint
    - name: nc_service_reversetunnel_state
      length: 0.5
      format: uint
    - name: nc_service_reversetunnel_substate
      length: 0.5
      format: uint
    - name: nc_service_wagmandriver_uptime
      length: 4
      format: epoch
    - name: nc_service_wagmandriver_exitcode
      length: 1
      format: uint
    - name: nc_service_wagmandriver_state
      length: 0.5
      format: uint
    - name: nc_service_wagmandriver_substate
      length: 0.5
      format: uint
    - name: nc_service_wwan_uptime
      length: 4
      format: epoch
    - name: nc_service_wwan_exitcode
      length: 1
      format: uint
    - name: nc_service_wwan_state
      length: 0.5
      format: uint
    - name: nc_service_wwan_substate
      length: 0.5
      format: uint

- id: 0x80
  conversion:
  params:
    - name: ep_node_id
      length: 12
      format: hex

- id: 0x81
  conversion:
  params:
    - name: ep_boot_id
      length: 32
      format: hex

- id: 0x82
  conversion:
  params:
    - name: ep_cpu_temp
      length: 2
      format: float_2

- id: 0x83
  conversion:
  params:
    - name: ep_ram_total
      length: 2
      format: float_2
    - name: ep_ram_free
      length: 2
      format: float_2

- id: 0x84
  conversion:
  params:
    - name: ep_current_disk_name
      length: 7
      format: str
    - name: ep_current_disk_type
      length: 2
      format: str
    - name: ep_alternate_disk_name
      length: 7
      format: str
    - name: ep_alternate_disk_type
      length: 2
      format: str
    - name: ep_partition1_total
      length: 2
      format: float_2
    - name: ep_partition1_used
      length: 1
      format: uint
    - name: ep_partition2_total
      length: 2
      format: float_2
    - name: ep_partition2_used
      length: 1
      format: uint
    - name: ep_partition3_total
      length: 2
      format: float_2
    - name: ep_partition3_used
      length: 1
      format: uint

- id: 0x85
  conversion:
  params:
    - name: ep_current_time
      length: 4
      format: epoch

- id: 0x86
  conversion:
  params:
    - name: ep_uptime
      length: 4
      format: uint
    - name: ep_idletime
      length: 4
      format: uint

- id: 0x87
  conversion:
  params:
    - name: ep_load_1
      length: 2
      format: float_2
    - name: ep_load_5
      length: 2
      format: float_2
    - name: ep_load_10
      length: 2
      format: float_2

- id: 0x88
  conversion:
  params:
    - name: ep_ipaddress
      length: 15
      format: str

- id: 0x89
  conversion:
  params:
    - name: ep_hbmode
      length: 6
      format: str

- id: 0x8A
  conversion:
  params:
    - name: ep_lock_fs
      length: 0.125
      format: uint
    - name: ep_lock_pw
      length: 0.125
      format: uint

- id: 0x8B
  conversion:
  params:
    - name: ep_devices_camera_bottom
      length: 0.125
      format: uint
    - name: ep_devices_camera_top
      length: 0.125
      format: uint
    - name: ep_devices_microphone
      length: 0.125
      format: uint

- id: 0x8C
  conversion:
  params:
    - name: ep_ver_core_mj
      length: 1
      format: uint
    - name: ep_ver_core_mi
      length: 1
      format: uint
    - name: ep_ver_core_p
      length: 1
      format: uint
    - name: ep_ver_edgeprocessor_mj
      length: 1
      format: uint
    - name: ep_ver_edgeprocessor_mi
      length: 1
      format: uint
    - name: ep_ver_edgeprocessor_p
      length: 1
      format: uint
    - name: ep_ver_pluginmanager_mj
      length: 1
      format: uint
    - name: ep_ver_pluginmanager_mi
      length: 1
      format: uint
    - name: ep_ver_pluginmanager_p
      length: 1
      format: uint

- id: 0x8D
  conversion:
  params:
    - name: ep_rabbitmq_queues_data
      length: 0.125
      format: uint
    - name: ep_rabbitmq_queues_images
      length: 0.125
      format: uint
    - name: ep_rabbitmq_exchanges_data
      length: 0.125
      format: uint
    - name: ep_rabbitmq_exchanges_images
      length: 0.125
      format: uint

- id: 0x8E
  conversion:
  params:
    - name: ep_service_rabbitmq_uptime
      length: 4
      format: epoch
    - name: ep_service_rabbitmq_exitcode
      length: 1
      format: uint
    - name: ep_service_rabbitmq_state
      length: 0.5
      format: uint
    - name: ep_service_rabbitmq_substate
      length: 0.5
      format: uint
    - name: ep_service_init_uptime
      length: 4
      format: epoch
    - name: ep_service_init_exitcode
      length: 1
      format: uint
    - name: ep_service_init_state
      length: 0.5
      format: uint
    - name: ep_service_init_substate
      length: 0.5
      format: uint
    - name: ep_service_heartbeat_uptime
      length: 4
      format: epoch
    - name: ep_service_heartbeat_exitcode
      length: 1
      format: uint
    - name: ep_service_heartbeat_state
      length: 0.5
      format: uint
    - name: ep_service_heartbeat_substate
      length: 0.5
      format: uint
'''
