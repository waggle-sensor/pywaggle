# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
'''
This module contains methods relating to the construction and interpretation of waggle packets. This module provides how to pack and unpack waggle message version 0.4.
The main functions to examine in this class are pack and unpack. This module handles
all CRC checking for the packets, so any sucessfully unpacked packet is known to be correct.
In Python3, data will be treated using bytearray.
'''
from crcmod.predefined import mkCrcFun
from struct import pack
import io
import time
import logging
import sys
import struct
import os.path

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Where each piece of information in a packet header is stored, by byte
# Total header size is 40 bytes.
HEADER_LOCATIONS = {
    "prot_ver"         : 0,
    "flags"            : 1,
    "len_body"         : 2,
    "time"             : 4,
    "msg_mj_type"      : 8,
    "msg_mi_type"      : 9,
    "ext_header"       : 10,    # 1 if puid presented, otherwise 0
    "optional_key"     : 11,    # Just 0
    "s_uniqid"         : 12,    # Find from /etc/waggle/hostname
    "r_uniqid"         : 20,    # Defined as 0 for the cloud
    "snd_session"      : 28,    # For Friday: just zero. Eventually automatic
    "resp_session"     : 30,    # Normally 0, sometimes used
    "snd_seq"          : 32,    # Tracked by this module
    "resp_seq"         : 35,    # Normally 0, sometimes used
    "crc-16"           : 38
}
#The length of each piece of data, in bytes
HEADER_BYTELENGTHS = {
    "prot_ver"         : 1,
    "flags"            : 1,
    "len_body"         : 2,
    "time"             : 4,
    "msg_mj_type"      : 1,
    "msg_mi_type"      : 1,
    "ext_header"       : 1,
    "optional_key"     : 1,
    "s_uniqid"         : 8,
    "r_uniqid"         : 8,
    "snd_session"      : 2,
    "resp_session"     : 2,
    "snd_seq"          : 3,
    "resp_seq"         : 3,
    "crc-16"           : 2
}

OPTIONAL_KEY_BIT_LOCATIONS = {
    "s_puid"           : 7,
    "r_puid"           : 6,
    "reserved1"        : 5,
    "reserved1"        : 4,
    "reserved1"        : 3,
    "reserved1"        : 2,
    "reserved1"        : 1,
    "mmsg"             : 0
}

OPTIONAL_KEY_BYTELENGTHS = {
    "s_puid"           : 4,
    "r_puid"           : 4,
    "reserved1"        : 0,
    "reserved1"        : 0,
    "reserved1"        : 0,
    "reserved1"        : 0,
    "reserved1"        : 0,
    "mmsg"             : 6
}

SIZE_2_TYPE =  [ 'c' for i in range(16)]
# '>' means big-endian
SIZE_2_TYPE[1] = '>B' # unsigned char
SIZE_2_TYPE[2] = '>H' # unsigned short
SIZE_2_TYPE[4] = '>I' # unsigned int
SIZE_2_TYPE[8] = '>q' # long long

#The total header length
HEADER_LENGTH = 40
FOOTER_LENGTH = 4
MAX_SEQ_NUMBER = pow(2,8*HEADER_BYTELENGTHS["snd_seq"])
MAX_PACKET_SIZE = 1024

VERSION = "0.4"

#Sequence becomes zero when the node starts again or when the package is
#reimported
SEQUENCE = 0

#The /etc/waggle folder has waggle specific information
S_UNIQUEID_HEX=None

#Create the CRC functions
crc32fun = mkCrcFun('crc-32')
crc16fun = mkCrcFun('crc-16')

crc16_position = HEADER_LOCATIONS['crc-16']

def nodeid_hexstr2int(node_id_hex):
    if type(node_id_hex) is str:
        node_id_hex = node_id_hex.encode('iso-8859-1')
    #return int.from_bytes(node_id_hex, byteorder='big')
    return int(node_id_hex, 16)

if os.path.isfile('/etc/waggle/node_id'):
    with open('/etc/waggle/node_id','r') as file_:
        S_UNIQUEID_HEX = file_.read().rstrip('\n')

    if len(S_UNIQUEID_HEX) != 2*HEADER_BYTELENGTHS["s_uniqid"]:
        logger.error("node id in /etc/waggle/node_id has wrong length (%d)" % (len(S_UNIQUEID_HEX)))
        sys.exit(1)

    S_UNIQUEID_HEX_INT= nodeid_hexstr2int(S_UNIQUEID_HEX)

    logger.debug("S_UNIQUEID_HEX:     %s" % (S_UNIQUEID_HEX))
    logger.debug("S_UNIQUEID_HEX_INT: %s" % (S_UNIQUEID_HEX_INT))
    logger.debug("S_UNIQUEID_HEX interpreted: %s" % (":".join("{:02x}".format(ord(c)) for c in S_UNIQUEID_HEX)))
else:
    logger.debug("file /etc/waggle/node_id not found")
    S_UNIQUEID_HEX_INT = 0

def _pack_int(value, size):
    return struct.pack(SIZE_2_TYPE[size], value)

def nodeid_int2hexstr(node_id):
    #return hex(node_id)[2:].zfill(2*HEADER_BYTELENGTHS["s_uniqid"])
    return "%0s"%format(node_id,'x').lower().zfill(2*HEADER_BYTELENGTHS["s_uniqid"])

def puid_hexstr2int(puid_hex):
    if type(puid_hex) is str:
        puid_hex = puid_hex.encode('iso-8859-1')
    return int(puid_hex, 16)

def puid_int2hexstr(puid, length):
    #return hex(node_id)[2:].zfill(2*HEADER_BYTELENGTHS["s_uniqid"])
    return "%0s"%format(puid,'x').lower().zfill(2*length)

def pack(header_data, message_data=""):
    """
        Takes header and message information and yields packets representing that data.

        :param dictionary header_data: A dictionary containing the header data
        :param string/FileObject message_data: The data to be packed into a Packet
        :yields: string
        :raises KeyError: A KeyError will be raised if the header_data dictionary is not properly formatted
    """
    global SEQUENCE
    global S_UNIQUEID_HEX_INT
    global VERSION

    #Generate the automatic fields
    auto_header = {
        "prot_ver"         : VERSION,
        "flags"            : (1,1,True),
        "len_body"         : len(message_data),
        "time"             : int(time.time()),
        "ext_header"       : 0,                   # PUID, MMSG, RESERVED
        "optional_key"     : [0,0,0,0,0,0,0,0],   # option flags
        "s_uniqid"         : S_UNIQUEID_HEX_INT,
        "r_uniqid"         : 0,                   # meaning the beehive server
        "snd_session"      : 0,
        "resp_session"     : 0,
        "snd_seq"          : SEQUENCE,
        "resp_seq"         : 0
    }
    #and update them with user-supplied values
    auto_header.update(header_data)

    # Optional flags processed here
    optional_key = {}
    optional_data = b''
    # The process order is important!
    # PUIDs presented with the length of 4
    if "s_puid" in auto_header and len(auto_header["s_puid"]) == 8:
        auto_header["ext_header"] = auto_header["optional_key"][OPTIONAL_KEY_BIT_LOCATIONS['s_puid']] = 1
        optional_data += bin_pack(puid_hexstr2int(auto_header["s_puid"]), OPTIONAL_KEY_BYTELENGTHS['s_puid'])

    if "r_puid" in auto_header and len(auto_header["r_puid"]) == 8:
        auto_header["ext_header"] = auto_header["optional_key"][OPTIONAL_KEY_BIT_LOCATIONS['r_puid']] = 1
        optional_data += bin_pack(puid_hexstr2int(auto_header["r_puid"]), OPTIONAL_KEY_BYTELENGTHS['r_puid'])

    #If it's a string, make it a file object
    # The encoding 'iso-8859-1' only covers char that is less than 256
    if(type(message_data) is str):
        message_data = io.BytesIO(message_data.encode('iso-8859-1'))
    else:
        message_data = io.BytesIO(message_data)
    #If it's under 1K, send it off as a single packet
    #Jump to the end of the file
    message_data.seek(0,2)

    header = None

    #See if it is less than 1K
    if(message_data.tell() < MAX_PACKET_SIZE):
        try:
            header = pack_header(auto_header)
        except KeyError as e:
            raise

        #Save the short message to a string
        message_data.seek(0)
        msg = bytes(optional_data) + message_data.read()
        message_data.close()

        #Calculate the CRC, pack it all up, and return the result.
        SEQUENCE = (SEQUENCE + 1) % MAX_SEQ_NUMBER
        msg_crc32 = bin_pack(crc32fun(msg),FOOTER_LENGTH)

        yield bytes(header) + msg + bytes(msg_crc32)

    #Multi-packet
    else:
        length = message_data.tell()
        message_data.seek(0)
        chunkNum = 1

        # Calculate number of chunks for the data
        numofchunks = length / MAX_PACKET_SIZE
        if length % MAX_PACKET_SIZE > 0:
            numofchunks += 1
        auto_header['ext_header'] = auto_header["optional_key"][OPTIONAL_KEY_BIT_LOCATIONS['mmsg']] = 1

        # Create smaller packets MAX_PACKET_SIZE bytes at a time, also attach packet number
        while length > MAX_PACKET_SIZE:
            try:
                header = pack_header(auto_header)
            except KeyError as e:
                raise
            msg = bytes(optional_data) + bin_pack(chunkNum,3) + bin_pack(numofchunks,3) + message_data.read(MAX_PACKET_SIZE)
            chunkNum += 1
            msg_crc32 = bin_pack(crc32fun(msg),FOOTER_LENGTH)
            yield bytes(header) + msg + bytes(msg_crc32)
            length -= MAX_PACKET_SIZE

        # Finish sending the message
        if length > 0:
            header = pack_header(auto_header)
            msg = bytes(optional_data) + bin_pack(chunkNum,3) + bin_pack(numofchunks,3) + message_data.read(MAX_PACKET_SIZE)
            SEQUENCE = (SEQUENCE + 1) % MAX_SEQ_NUMBER
            msg_crc32 = bin_pack(crc32fun(msg),FOOTER_LENGTH)
            yield bytes(header) + msg + bytes(msg_crc32)

def unpack(packet):
    """
        Turns a packet object into a tuple containing the header data and message body

        :param string packet: The packet data to be unpacked
        :rtype: tuple(dictionary, string)
        :raises IOError: An IOError will be raised if a CRC fails in the packet
        :raises KeyError: An IndexError will be raised if a packet header is the wrong length
    """
    #crc32fun = mkCrcFun('crc-32')
    header = None
    if(crc32fun(packet[HEADER_LENGTH:-FOOTER_LENGTH]) != _bin_unpack(packet[-FOOTER_LENGTH:])):
        raise IOError("Packet body CRC-32 failed.")
    try:
        header = _unpack_header(packet[:HEADER_LENGTH])
    except Exception as e:
        logger.error("_unpack_header failed: "+str(e))
        raise

    # parse optional keys
    optional_header = None
    optional_header_length = 0
    if header['ext_header'] == 1:
        try:
            (optional_header, optional_header_length) = _unpack_optional_header(header['optional_key'], packet[HEADER_LENGTH:-FOOTER_LENGTH])
        except Exception as e:
            logger.error("_unpack_sec_header failed: " + str(e))
            raise

    return (header, optional_header, packet[HEADER_LENGTH+optional_header_length:-FOOTER_LENGTH])

#def print_packet(packet):
#    (header, body) = unpack(packet)
#
#    for key,value in header.items():
#        logger.debug("%s: %d", (key, value))
#
#    logger.debug("body: %s\n" %(body))
#

def pack_header(header_data):
    """
        Attempt to pack the data from the header_data dictionary into binary format according to Waggle protocol.

        :param dictionary header_data: The header data to be serialized
        :rtype: string
        :raises KeyError: An exception will be raised if the provided dictionary does not contain required information
    """

    header = bytearray()
    try:
        header.append(_pack_version(header_data["prot_ver"]))                                                   # Serialize protocol version
        header.append(_pack_flags(header_data["flags"]))                                                        # Packet flags
        header += bin_pack(header_data["len_body"],HEADER_BYTELENGTHS["len_body"])          # Length of message body
        header += bin_pack(header_data["time"],HEADER_BYTELENGTHS["time"])                  # Timestamp
        header += bin_pack(header_data["msg_mj_type"], HEADER_BYTELENGTHS["msg_mj_type"])   # Message Major Type
        header += bin_pack(header_data["msg_mi_type"], HEADER_BYTELENGTHS["msg_mi_type"])   # Message Minor Type
        header += bin_pack(header_data["ext_header"], HEADER_BYTELENGTHS["ext_header"])     # Optional extended header
        header += _pack_optional_key(header_data["optional_key"])        # Optional flag header
        header += bin_pack(header_data["s_uniqid"],HEADER_BYTELENGTHS["s_uniqid"])          # Sender unique ID
        header += bin_pack(header_data["r_uniqid"],HEADER_BYTELENGTHS["r_uniqid"])          # Recipient unique ID
        header += bin_pack(header_data["snd_session"],HEADER_BYTELENGTHS["snd_session"])    # Send session number
        header += bin_pack(header_data["resp_session"],HEADER_BYTELENGTHS["resp_session"])  # Response session number
        header += bin_pack(header_data["snd_seq"],HEADER_BYTELENGTHS["snd_seq"])            # Send sequence number
        header += bin_pack(header_data["resp_seq"],HEADER_BYTELENGTHS["resp_seq"])          # Response sequence number
    except KeyError as e:
        raise KeyError("Header packing failed. The required dictionary entry %s was missing!" % str(e))


    #Compute the header CRC and stick it on the end
    #crc16 = mkCrcFun('crc-16')
    header += bin_pack(crc16fun(header) ,HEADER_BYTELENGTHS['crc-16'])

    return header


def get_header(packet):
    """
        Given a complete packet, this method will return the header as a dictionary.

        :param string packet: A complete packet.
        :rtype: dictionary
        :raises IndexError: An IndexError will be raised if the packed header is not 40 bytes long
        :raises IOError: An IOError will be raised if the packet header fails its CRC-16 check
    """
    try:
        header = _unpack_header(packet[:HEADER_LENGTH])
        return header
    except Exception as e:
        raise


"""
(bytearray header) Sets header field in an bytearray. Value also has to be an bytearray.
"""
def set_header_field(header_bytearray, field, value):
    if type(value) is str:
        value = value.encode('iso-8859-1')
    try:
        field_position = HEADER_LOCATIONS[field]
        field_length = HEADER_BYTELENGTHS[field]
    except Exception as e:
        logger.error("Field name unknown: %s" % (str(e)) )
        raise

    if len(value) != field_length:
        e = ValueError("data length: %d bytes, but field is of size: %d bytes (field: %s)" % (len(value), field_length, field) )
        logger.error(str(e))
        raise e

    if (len(header_bytearray) != HEADER_LENGTH):
        e = ValueError("header length is not correct: %d vs HEADER_LENGTH=%d" %(len(header_bytearray), HEADER_LENGTH) )
        logger.error(str(e))
        raise e

    for i in range(field_length):
        header_bytearray[field_position+i] = value[i]



"""
    (bytearray header) Calculates the header crc and accordingly sets the crc-16 field.
"""
def write_header_crc(header_bytearray):

    new_crc = crc16fun(bytes(header_bytearray[:crc16_position]))

    new_crc_packed = bin_pack(new_crc,HEADER_BYTELENGTHS['crc-16'])

    set_header_field(header_bytearray, 'crc-16', new_crc_packed)



def bin_pack(n, size):
    """
        Takes in an int n and returns it in binary string format of a specified length

        :param int n: The integer to be converted to binary
        :param int size: The number of bytes that the integer will be represented with
        :rtype: string
    """
    packed = bytearray(size)

    for i in range(1, size + 1):
        packed[-i] = 0xff & (n >> (i - 1)*8)

    #return str(packed)    # for python2
    return packed # for python3





"""
-------------------------------------------------------------------------------------------------------------------
                                          private methods start here
-------------------------------------------------------------------------------------------------------------------
"""


def _unpack_header(packed_header):
    """
        Given a packed header, this method will return a dictionary with the unpacked contents.

        :param bytes packed_header: A string representing a waggle header
        :rtype: Dictionary
        :raises IndexError: An IndexError will be raised if the packed header is not 40 bytes long
        :raises IOError: An IOError will be raised if the packet header fails its CRC-16 check
    """

    # Check header length
    if len(packed_header) != HEADER_LENGTH:
        raise IndexError("Tried to unpack a waggle header that was %d instead of %d bytes long." % (len(packed_header), HEADER_LENGTH ) )

    header_IO = io.BytesIO(packed_header)

    #Check the CRC
    #CRC16 = mkCrcFun('CRC-16')
    header_IO.seek(HEADER_LOCATIONS["crc-16"])
    headerCRC = header_IO.read(2)
    if(crc16fun(packed_header[:-2]) != _bin_unpack(headerCRC)):
        raise IOError("Header CRC-16 check failed")
    header_IO.seek(0)

    # The header passed the CRC check. Hooray! Now return a dictionary containing the info.
    header = {
        "prot_ver"     : _unpack_version(header_IO.read(HEADER_BYTELENGTHS["prot_ver"])),        # Load protocol version
        "flags"        : _unpack_flags(header_IO.read(HEADER_BYTELENGTHS["flags"])),             # Load flags
        "len_body"     : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["len_body"])),            # Load message body length
        "time"         : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["time"])),                # Load time
        "msg_mj_type"  : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["msg_mj_type"])),         # Load message major type
        "msg_mi_type"  : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["msg_mi_type"])),         # Load message minor type
        "ext_header"   : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["ext_header"])),          # Load extended header
        "optional_key" : _unpack_optional_key(header_IO.read(HEADER_BYTELENGTHS["optional_key"])),          # Load extended header
        "s_uniqid"     : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["s_uniqid"])),            # Load sender unique ID
        "r_uniqid"     : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["r_uniqid"])),            # Load recipient unique ID
        "snd_session"  : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["snd_session"])),         # Load send session number
        "resp_session" : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["resp_session"])),        # Load recipient session number
        "snd_seq"      : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["snd_seq"])),             # Load send sequence number
        "resp_seq"     : _bin_unpack(header_IO.read(HEADER_BYTELENGTHS["resp_seq"]))             # Load recieve sequence number
    }

    header_IO.close()
    return header

def _unpack_optional_header(optional_key, message_body):
    """
        For internal use.
        Takes a tuple representing the flags,extract information from the message body, and finally put them to a dictionary.

        :param tuple optional_key: tuple(int, int, int, int, int, int, int, int)
        :param string message_body:
        :rtype Dictionary
    """
    length = 0
    available_flags = []
    for key in OPTIONAL_KEY_BIT_LOCATIONS:
        index = OPTIONAL_KEY_BIT_LOCATIONS[key]
        if optional_key[index] == 1:
            available_flags.append(key)
            length += OPTIONAL_KEY_BYTELENGTHS[key]

    # Check header length
    if len(message_body) < length:
        raise IndexError("Tried to unpack a waggle optional header that was %d instead of %d bytes long." % (len(message_body), length ) )

    optional_header_IO = io.BytesIO(message_body)
    print(available_flags)
    optional_header = {}
    if "s_puid" in available_flags:

        optional_header["s_puid"] = _bin_unpack(optional_header_IO.read(OPTIONAL_KEY_BYTELENGTHS["s_puid"]))

    if "r_puid" in available_flags:
        optional_header["r_puid"] = _bin_unpack(optional_header_IO.read(OPTIONAL_KEY_BYTELENGTHS["r_puid"]))

    if "mmsg" in available_flags:
        optional_header["mmsg"] = _bin_unpack(optional_header_IO.read(OPTIONAL_KEY_BYTELENGTHS["mmsg"]))


    optional_header_IO.close()
    return (optional_header, length)

def _pack_flags(flags):
    """
        For internal use.
        Takes a tuple representing the message priorities and FIFO/LIFO preference and packs them to one byte.

        :param tuple(int,int,bool) flags:
        :rtype: string
    """
    return (flags[0] << 5) | (flags[1] << 2) | (flags[2] << 1)


def _unpack_flags(flagByte):
    """
        For internal use.
        Takes in the priority byte from the header and returns a tuple containing the correct information.

        :param string flagByte: The priority byte from the header
        :rtype: Tuple(Int, Int, Bool)
    """
    return ((ord(flagByte) & 0xe0) >> 5, (ord(flagByte) & 0x1c) >> 2, bool((ord(flagByte) & 0x02) >> 1))

def _pack_optional_key(optional_key):
    """
        For internal use.
        Takes a dictionary representing entities in optional key and packs them to one byte.

        :param tuple(int, int, int, int, int, int, int, int) flags:
        :rtype: string
    """
    return _pack_int((optional_key[7] << 7) | (optional_key[6] << 6) | (optional_key[5] << 5) | (optional_key[4] << 4) | (optional_key[3] << 3) | (optional_key[2] << 2) | (optional_key[1] << 1) | (optional_key[0] & 0x01), 1)


def _unpack_optional_key(optional_keyByte):
    """
        For internal use.
        Takes in the optional key byte from the header and returns a tuple containing the correct information.

        :param string flagByte: The priority byte from the header
        :rtype: tuple(int, int, int, int, int, int, int, int)
    """
    return ((ord(optional_keyByte) & 0x01), (ord(optional_keyByte) & 0x02) >> 1, (ord(optional_keyByte) & 0x04) >> 2, (ord(optional_keyByte) & 0x08) >> 3, (ord(optional_keyByte) & 0x10) >> 4, (ord(optional_keyByte) & 0x20) >> 5, (ord(optional_keyByte) & 0x40) >> 6, (ord(optional_keyByte) & 0x80) >> 7)

def _unpack_version(version):
    """
        For internal use.
        Returns the protocol in string form.

        :param string version: byte representing the version
        :rtype: string
    """
    v = ord(version)
    major = v & 0xf0
    minor = v & 0x0f

    # return the version in human-readable form. For example: "0x03" becomes "0.3".
    return str(major) + "." + str(minor)

def _pack_version(version):
    """
        For internal use.
        Returns the protocol as a binary

        :param string version: The version in human-readable format, i.e. "0.3"
        :rtype: The protocol version as a 1 byte string
    """
    versions = version.split(".")
    major = int(versions[0])
    minor = int(versions[1])

    return (major << 4) | (0xf & minor)




def _bin_unpack(string):
    """
        For internal use.
        Takes in a string and returns it in integer format

        :param string string: The binary string to read
        :rtype: int
    """
    x = 0

    for i in range(1, len(string) + 1):
        x = x | (string[-i] << (i - 1)*8)

    return x
