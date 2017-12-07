# Conversion for chemsense

# chemsense version2, no data of IMU is comming from chemsense --> chemsense FW issue

def convert(value):
    raw_s = value['chemsense_raw']

    textlist = raw_s.split(' ')

    chem_dict = {}

    for i in range(len(textlist)):
        a_data = textlist[i].split('=')

        if len(a_data) == 2:
            key = a_data[0]
            val = a_data[1]

            if 'SQN' in key:
                continue
            elif 'BAD' in key:
                chem_dict['ChemMac'] = val
            elif 'SH' in key or 'HD' in key or 'LP' in key or 'AT' in key or 'LT' in key:
                val = float(val)/100.0
                if 'T' in key:
                    chem_dict[key] = (val, 'C')
                elif 'P' in key:
                    chem_dict[key] = (val, 'hPa')
                else:
                    chem_dict[key] = (val, '%RH')
            elif 'SVL' in key or 'SIR' in key or 'SUV' in key:
                chem_dict[key] = (val, 'raw')
            else:
                chem_dict[key] = (int(val), 'raw')

        if len(chem_dict) == 0:
            chem_dict['chemMac'] = ('Chemsense not included', 'No unit')
    return chem_dict
