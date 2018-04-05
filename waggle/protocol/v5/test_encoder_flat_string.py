import unittest
from waggle.protocol.v5.decoder import decode_frame
from waggle.protocol.v5.encoder import encode_frame_from_flat_string


def flatten_sensor_values(sensor_values):
    flattened_values = {}

    for sensor_values in sensor_values.values():
        flattened_values.update(sensor_values)

    return flattened_values


class WaggleProtocolTestUnit(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(decode_frame(encode_frame_from_flat_string('')), {})

    def test_encode(self):
        text = '''
ep_alternate_disk_type M
ep_boot_id 58baa437795742ba837aec382001e358
ep_cpu_temp 74000
ep_current_disk_type S
ep_current_time 1522942102
ep_devices_camera_bottom Y
ep_devices_camera_top Y
ep_devices_microphone N
ep_hbmode w
ep_idletime 967034
ep_load_1 1.74
ep_load_10 1.65
ep_load_5 1.68
ep_lock_fs N
ep_lock_pw Y
ep_machine_id dc87f36fc06c441a85ff7269ba4d50fb
ep_partition1_total 129
ep_partition1_used 8
ep_partition2_total 7254
ep_partition2_used 6201
ep_partition3_total 7318
ep_partition3_used 286
ep_rabbitmq_exchanges_data N
ep_rabbitmq_exchanges_images Y
ep_rabbitmq_queues_data N
ep_rabbitmq_queues_images Y
ep_ram_free 1519216
ep_ram_total 2038608
ep_service_heartbeat_exitcode 0
ep_service_heartbeat_state a
ep_service_heartbeat_substate r
ep_service_heartbeat_uptime 1522795300
ep_service_init_exitcode 1
ep_service_init_state i
ep_service_init_substate d
ep_service_init_uptime 1522795300
ep_service_rabbitmq_exitcode 0
ep_service_rabbitmq_state a
ep_service_rabbitmq_substate r
ep_service_rabbitmq_uptime 1522876954
ep_uptime 146759
ep_ver_core_mi 8
ep_ver_core_mj 2
ep_ver_core_p 2
ep_ver_edge_processor_mi 8
ep_ver_edge_processor_mj 2
ep_ver_edge_processor_p 2
nc_alternate_disk_type M
nc_beehive_ping Y
nc_beehive_sshd Y
nc_boot_id 1bc757c38743411ba3ef9d11267bb576
nc_cpu_temp 47000
nc_current_disk_type S
nc_current_time 1522942084
nc_devices_alphasense N
nc_devices_metsense Y
nc_devices_modem N
nc_devices_wagman Y
nc_hbmode w
nc_idletime 558383
nc_load_1 0.5
nc_load_10 0.5
nc_load_5 0.51
nc_local_sshd Y
nc_lock_fs N
nc_lock_pw Y
nc_machine_id 7a18bd66c48041c9a76bb5890b64483d
nc_partition1_total 129
nc_partition1_used 9
nc_partition2_total 7254
nc_partition2_used 1147
nc_partition3_total 7318
nc_partition3_used 1210
nc_rabbitmq_exchanges_data Y
nc_rabbitmq_queues_data Y
nc_rabbitmq_shovels_data Y
nc_rabbitmq_shovels_images Y
nc_ram_free 332136
nc_ram_total 823656
nc_service_epoch_exitcode 0
nc_service_epoch_state a
nc_service_epoch_substate r
nc_service_epoch_uptime 1522794958
nc_service_heartbeat_exitcode 0
nc_service_heartbeat_state a
nc_service_heartbeat_substate r
nc_service_heartbeat_uptime 1522794958
nc_service_init_exitcode 1
nc_service_init_state i
nc_service_init_substate d
nc_service_init_uptime 1522794958
nc_service_rabbitmq_exitcode 0
nc_service_rabbitmq_state a
nc_service_rabbitmq_substate r
nc_service_rabbitmq_uptime 1522874429
nc_service_reversetunnel_exitcode 0
nc_service_reversetunnel_state a
nc_service_reversetunnel_substate r
nc_service_reversetunnel_uptime 1522795019
nc_service_wagmandriver_exitcode 0
nc_service_wagmandriver_state a
nc_service_wagmandriver_substate r
nc_service_wagmandriver_uptime 1522795273
nc_service_wwan_exitcode 1
nc_service_wwan_state a
nc_service_wwan_substate a
nc_service_wwan_uptime 1522942081
nc_uptime 147143
nc_ver_core_mi 8
nc_ver_core_mj 2
nc_ver_core_p 2
nc_ver_nodecontroller_mi 8
nc_ver_nodecontroller_mj 2
nc_ver_nodecontroller_p 2
nc_ver_plugin_manager_mi 8
nc_ver_plugin_manager_mj 2
nc_ver_plugin_manager_p 2
        '''

        encoded_data = encode_frame_from_flat_string(text, verbose=True)
        decoded_data = decode_frame(encoded_data)

        values = flatten_sensor_values(decoded_data)
        print(values)

        self.assertAlmostEqual(values['nc_load_1'], 0.74)
        self.assertAlmostEqual(values['nc_load_5'], 0.53)
        self.assertAlmostEqual(values['nc_load_10'], 0.45)
        self.assertAlmostEqual(values['nc_ram_total'], 8046136)
        self.assertAlmostEqual(values['nc_ram_free'], 291328)
        self.assertAlmostEqual(values['net_broadband_rx'], 123456)
        self.assertAlmostEqual(values['net_broadband_tx'], 654321)

        self.assertEqual(values['wagman_ver_git'], '1ef3')
        self.assertEqual(values['nc_boot_id'], '12345678901234567890123456789012')


if __name__ == '__main__':
    unittest.main()
