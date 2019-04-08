# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
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

xu4_ip_link = '''
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: enx001e06324dcb: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 00:1e:06:32:4d:cb brd ff:ff:ff:ff:ff:ff
'''

xu4_cpuinfo = '''
processor	: 0
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 84.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x0
CPU part	: 0xc07
CPU revision	: 3

processor	: 1
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 84.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x0
CPU part	: 0xc07
CPU revision	: 3

processor	: 2
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 84.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x0
CPU part	: 0xc07
CPU revision	: 3

processor	: 3
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 84.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x0
CPU part	: 0xc07
CPU revision	: 3

processor	: 4
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 120.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x2
CPU part	: 0xc0f
CPU revision	: 3

processor	: 5
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 120.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x2
CPU part	: 0xc0f
CPU revision	: 3

processor	: 6
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 120.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x2
CPU part	: 0xc0f
CPU revision	: 3

processor	: 7
model name	: ARMv7 Processor rev 3 (v7l)
BogoMIPS	: 120.00
Features	: swp half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x2
CPU part	: 0xc0f
CPU revision	: 3

Hardware	: ODROID-XU3
Revision	: 0100
Serial		: 0000000000000000
'''


class TestPlatform(unittest.TestCase):

    def test_scan_hardware(self):
        self.assertEqual(scan_hardware(c1p_cpuinfo), 'C1+')
        self.assertEqual(scan_hardware(xu4_cpuinfo), 'XU4')

    def test_scan_macaddr(self):
        self.assertEqual(scan_macaddr(c1p_ip_link), '0000001e0610e34e')
        self.assertEqual(scan_macaddr(xu4_ip_link), '0000001e06324dcb')


if __name__ == '__main__':
    unittest.main()
