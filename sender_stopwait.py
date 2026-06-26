
import socket
import time
import os
import argparse
from support import DATA_TYPE, ACK_TYPE, START_TYPE, END_TYPE, HEADER_LENGTH, MAX_PAYLOAD_LENGTH, create_packet, unpack_packet, load_data
 
sock = None
retransmissions = 0
destination = None

"""
Sends A Packet Using The Stop And Wait Approach

Params:
    packet: Data To Be Sent
    expected_ack: The ACK Number To Wait For
    max_attempts: Transmissions Attempted Before Error
"""
def send_stopwait(packet:bytes, expected_ack:int, max_attempts:int=20):
    global retransmissions
    attempts = 0

    while attempts < max_attempts:
        sock.sendto(packet, destination)
        attempts += 1
        
        try:
            #Recieve Packet
            recieved_packet, _ = sock.recvfrom(MAX_PAYLOAD_LENGTH + HEADER_LENGTH)
            packet_type, __, recieved_ack, __ = unpack_packet(recieved_packet)

            #Accept If Correct ACK
            if packet_type == ACK_TYPE and recieved_ack == expected_ack:
                print(f"[Sender]: ACK{expected_ack} Recieved")
                return 
            else:
                print(f"[Sender]: ----Recieved Unexpected ACK{recieved_ack}")

        except socket.timeout:
            print("[Sender]: ----Packet Timeout, Resending")
            retransmissions += 1

    raise Exception(f"ACK{expected_ack} Not Recieved")
 

"""
Sends A File Or Specified Number Of Bytes Using The Stop And Wait Method
"""
def main():
    global destination
    global sock

    try:
        #Arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("--host",                default="127.0.0.1")
        ap.add_argument("--port",    type=int,   default=5005)
        ap.add_argument("--file",    type=str,   default=None)
        ap.add_argument("--size",    type=int,   default=51200)
        ap.add_argument("--timeout", type=float, default=0.5)
        args = ap.parse_args()

        #Create UDP Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(args.timeout)
        
        destination = (args.host, args.port)
        
        #Extract File Data Into Packets
        file_packets, file_name, file_size, total_packets = load_data(args.file, args.size)
        print(f"[Sender]: Sending {file_name} (Bytes:{file_size}, Packets:{total_packets} + 2)")

        #Start
        start_time = time.time()
        send_stopwait(packet=create_packet(START_TYPE,0,0,file_name.encode()), expected_ack=0)   
    
        #Data
        for i, chunk in enumerate(file_packets):
            send_stopwait(packet=create_packet(DATA_TYPE, i+1, 0, chunk), expected_ack=i+1)
    
        #End
        send_stopwait(packet=create_packet(END_TYPE,total_packets+1, 0, b""), expected_ack=total_packets+1)
        total_time = time.time() - start_time
        throughput = file_size/total_time/1000
        print(f"""[Sender]: Send Successfully (Time:{total_time:.2f}s, Retransmissions:{retransmissions}, Throughput:{throughput:,.2f} mbps)""")

    except Exception as e:
        print(f"[Sender]: ERROR {str(e)}")
    
    finally:
        if sock is not None:
            sock.close()
            print("[Sender]: Socket Closed")

if __name__ == "__main__":
    main()
 