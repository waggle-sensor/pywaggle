# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
'''
This module contains a few utilities that autogenerate complete simple packets,
such as ping and time request packets.
'''
from waggle.protocol.utils.gPickler import gPickle
from waggle.protocol.PacketHandler import *


def make_packet(argDict):
    """
    Makes a packet according to the major and minor type of the data and returns waggle message(s) for the data.
    :param Dictionary argDict: all arguments to make waggle message
    :rtype string: one or more waggle message
    """
    try:
        mj_type = argDict["msg_mj_type"]
        mi_type = argDict["msg_mi_type"]

        # Get function info
        func = func_dict[(mj_type, mi_type)][0]
        mandatoryArgs = func_dict[(mj_type, mi_type)][1]
        optionalArgs = func_dict[(mj_type, mi_type)][2]

        args = [argDict[item] for item in mandatoryArgs]

        # This only works for string type arguments
        for item in optionalArgs:
            if item in argDict:
                args.append(argDict[item])
            else:
                args.append("")

        return func(*args)
    except KeyError as e:
        raise

def make_ping_packet(s_puid = "", r_puid = ""):
    """
        Returns a simple ping request packet.

        :rtype: string
    """
    header_dict = {
        "msg_mj_type" : ord('p'),
        "msg_mi_type" : ord('r')
    }
    if s_puid:
        header_dict['s_puid'] = s_puid
    if r_puid:
        header_dict['r_puid'] = r_puid
    return pack(header_dict)

def make_time_packet(s_puid = "", r_puid = ""):
    """
        Returns a simple time request packet.

        :rtype: string
    """
    header_dict = {
        "msg_mj_type" : ord('t'),
        "msg_mi_type" : ord('r')
    }
    if s_puid:
        header_dict['s_puid'] = s_puid
    if r_puid:
        header_dict['r_puid'] = r_puid
    return pack(header_dict)

def make_data_packet(data, s_puid = "", r_puid = ""):
    """
    Compresses sensor data and returns a sensor data packet.

    :param data: sensor data
    :rtype: string
    """
    msg = gPickle(data)
    header_dict = {
        "msg_mj_type" : ord('s'),
        "msg_mi_type" : ord('d')
        }
    if s_puid:
        header_dict['s_puid'] = s_puid
    if r_puid:
        header_dict['r_puid'] = r_puid
    return pack(header_dict, message_data = msg)

def registration_packet(queuename, s_puid = "", r_puid = ""):
    """
        Returns a registration request packet.

        :rtype: string
    """

    header_dict = {
        "msg_mj_type" : ord('r'),
        "msg_mi_type" : ord('r')
        }
    msg = str(QUEUENAME)
    if s_puid:
        header_dict['s_puid'] = s_puid
    if r_puid:
        header_dict['r_puid'] = r_puid
    return pack(header_dict, message_data = msg)

def make_config_reg(config):
    """
        Returns a configuration registration packet.

        :param config: node configuration file
        :rtype: string

    """
    header_dict = {
        "msg_mj_type" : ord('r'),
        "msg_mi_type" : ord('n')
        }
    return pack(header_dict, message_data = config)

def make_GN_reg(recp_ID):
    """
        Returns a guestnode registration packet to send to the node controller.
    """

    header_dict = {
        "msg_mj_type" : ord('r'),
        "msg_mi_type" : ord('r'),
        "r_uniqid" : recp_ID

        }


    return pack(header_dict, message_data = '')

def make_registration_response(recp_ID, s_uniqid = "", s_puid = "", r_puid = "", resp_session = "", data = ""):
    """
        Returns registration response. Normally used in Beehive server side.
        :param recp_ID: Unique ID of the message recipient
        :rtype: string
    """

    header_dict = {
        "msg_mj_type" : ord('r'),
        "msg_mi_type" : ord('a'),
        "r_uniqid" : recp_ID
    }
    if s_uniqid:
        header_dict['s_uniqid'] = s_uniqid
    if s_puid:
        header_dict['s_puid'] = s_puid
    if r_puid:
        header_dict['r_puid'] = r_puid
    if resp_session:
        header_dict['resp_session'] = resp_session

    return pack(header_dict, data)

#TODO may want to add an additional option argument to specify sender_id so that server can send a de-registration message for a GN
def deregistration_packet(r_uniqid, s_puid = "", r_puid = ""):
    """
        Returns a deregistration request packet.

        :param recp_ID: Unique ID of the message recipient
        :rtype: string
    """

    header_dict = {
        "msg_mj_type" : ord('r'),
        "msg_mi_type" : ord('d'),
        "r_uniqid" : r_uniqid
        }
    if s_puid:
        header_dict['s_puid'] = s_puid
    if r_puid:
        header_dict['r_puid'] = r_puid

    return pack(header_dict, message_data = '')

# Dictionary of supported fuctions
# Mj/Mi types mapped to name of the function, mandatory args, and optional args
func_dict = {('p', 'r'): (make_ping_packet, (), ('s_puid', 'r_puid')),
             ('t', 'r'): (make_time_packet, (), ('s_puid', 'r_puid')),
             ('s', 'd'): (make_data_packet, ('data',), ('s_puid', 'r_puid')),
             ('r', 'r'): (registration_packet, ('data',), ('s_puid', 'r_puid')),
             ('r', 'n'): (make_config_reg, ('data',), ()),
             ('r', 'a'): (make_registration_response, ("r_uniqid",), ("s_uniqid", "s_puid", "r_puid", "resp_session", "data")),
             ('r', 'd'): (deregistration_packet, ("r_uniqid",), ('s_puid', 'r_puid'))}
