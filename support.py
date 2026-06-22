import struct
import os






##############################
# HEADER
# 
# 1 Byte  - Type (DATA, ACK, START, END)
# 4 Bytes - Packet Sequence Number
# 4 Bytes - Acknowledgement
# 4 Bytes - Payload Length
#############################

TYPE_INDEX = 0
SEQ_INDEX  = 1
ACK_INDEX  = 2
LEN_INDEX  = 3

DATA_TYPE = 0
ACK_TYPE = 1
START_TYPE = 2
END_TYPE = 3


HEADER_FORMAT = "!BIII"
HEADER_LENGTH =  1 + 4 + 4 + 4

MAX_PAYLOAD_LENGTH = 1024


def create_packet(packet_type, seq, ack, payload):
    return struct.pack(HEADER_FORMAT, packet_type, seq, ack, len(payload)) + payload

def unpack_packet(packet):
    header = struct.unpack(HEADER_FORMAT, packet[:HEADER_LENGTH])
    
    return header[TYPE_INDEX], header[SEQ_INDEX], header[ACK_INDEX], packet[HEADER_LENGTH:]




def load_data(file:str, size:int=0):
    if file:
        try:
            with open(file, "rb") as fh:
                file_payload = fh.read()
                file_name = os.path.basename(file)
                file_size = len(file_payload)
        except Exception:
            raise Exception("Specified Path Doesnt Exist")
    else:
        file_payload = os.urandom(size)
        file_name = f"RandomFileData({size}).bin"
        file_size = size

    file_packets = [file_payload[i:i + MAX_PAYLOAD_LENGTH] for i in range(0, file_size, MAX_PAYLOAD_LENGTH)]
    total_packets = len(file_packets)

    return file_packets, file_name, file_size, total_packets
