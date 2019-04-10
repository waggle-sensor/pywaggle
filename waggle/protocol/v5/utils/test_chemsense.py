# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import unittest
import pprint
from chemsense import convert


testdata = [
    'BAD=5410EC38A62B SQN=DC SHT=83 SHH=4459 HDT=78 HDH=5000 LPT=265 LPP=99849 SUV=1 SVL=260 SIR=250 BAD=5410EC38A62B SQN=DD IRR=2399 IAQ=21040 SO2=-73 H2S=246 OZO=5316 NO2=849 CMO=3503 BAD=5410EC38A62B SQN=DE AT0=32 AT1=58 AT2=116 AT3=161 LTM=6545',
    'BAD=5410EC38A62B SQN=F0 SHT=83 SHH=4368 HDT=78 HDH=5039 LPT=264 LPP=99854 SUV=15 SVL=294 SIR=230 BAD=5410EC38A62B SQN=F1 IRR=2492 IAQ=20109 SO2=-1161 H2S=-1116 OZO=5148 NO2=1493 CMO=3272 BAD=5410EC38A62B SQN=F2 AT0=32 AT1=58 AT2=116 AT3=161 LTM=6545',
    'BAD=5410EC38A62B SQN=4 SHT=83 SHH=4404 HDT=78 HDH=5039 LPT=266 LPP=99845 SUV=0 SVL=249 SIR=265 BAD=5410EC38A62B SQN=5 IRR=2068 IAQ=20305 SO2=-663 H2S=318 OZO=4361 NO2=508 CMO=3195 BAD=5410EC38A62B SQN=6 AT0=32 AT1=58 AT2=116 AT3=161 LTM=6545',
]

if __name__ == '__main__':
    for data in testdata:
        value = {'chemsense_raw': data}
        pprint.pprint(convert(value))
