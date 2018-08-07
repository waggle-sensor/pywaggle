import unittest
from __init__ import scan_hardware
from __init__ import scan_macaddr


c1p_ip_link = '''
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
link/ether 00:1e:06:10:e3:4e brd ff:ff:ff:ff:ff:ff
3: sit0: <NOARP> mtu 1480 qdisc noop state DOWN mode DEFAULT group default
link/sit 0.0.0.0 brd 0.0.0.0
4: ip6tnl0@NONE: <NOARP> mtu 1452 qdisc noop state DOWN mode DEFAULT group default
link/tunnel6 :: brd ::
5: enxa0cec807b4ee: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN mode DEFAULT group default qlen 1000
link/ether a0:ce:c8:07:b4:ee brd ff:ff:ff:ff:ff:ff
'''

c1p_cpuinfo = '''
Processor	: ARMv7 Processor rev 1 (v7l)
processor	: 0
BogoMIPS	: 3.27

processor	: 1
BogoMIPS	: 3.27

processor	: 2
BogoMIPS	: 3.27

processor	: 3
BogoMIPS	: 3.27

Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x0
CPU part	: 0xc05
CPU revision	: 1

Hardware	: ODROIDC
Revision	: 000a
Serial		: 1b00000000000000
'''


class TestPlatform(unittest.TestCase):

    def test_hardware(self):
        self.assertEqual(scan_hardware(c1p_cpuinfo), 'C1+')

    def test_macaddr(self):
        self.assertEqual(scan_macaddr(c1p_ip_link), '0000001e0610e34e')


if __name__ == '__main__':
    unittest.main()
