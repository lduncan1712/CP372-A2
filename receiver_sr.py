"""
-------------------------------------------------------
Assignment 02 BONUS, Receiver Selective Repeat
-------------------------------------------------------
Author:  Group 30
__updated__ = "2026-06-26"
-------------------------------------------------------
"""
import socket
import argparse
import random
import os
from support import DATA_TYPE, ACK_TYPE, START_TYPE, END_TYPE, create_packet, unpack_packet

def main():

    #Arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--host",             default="127.0.0.1")
    ap.add_argument("--port", type=int,   default=5005)
    ap.add_argument("--loss", type=float, default=0.0)
    ap.add_argument("--outdir",           default=".")
    ap.add_argument("--window", type=int, default=10)
    args = ap.parse_args()

    #Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))
    print(f"[Reciever] Awaiting Packets From {args.host}:{args.port}  (Loss:{args.loss})")

    #Variables
    expected_sequence = 0
    recieved_file = None
    file_name = None
    buffer = {}
    end_sequence = None

    #Await Packets
    while True:

        #Extract Packet
        packet, addr = sock.recvfrom(65535)
        packet_type, sequence_number, ack, payload = unpack_packet(packet)

        #Packet Loss (Drop Before Processing So No ACK Is Sent)
        if packet_type == DATA_TYPE and random.random() < args.loss:
            print("[Reciever]: ----Packet Lost Intentionally")
            continue

        #Packet Within Window
        if expected_sequence <= sequence_number < expected_sequence + args.window:

            #Begin File
            if packet_type == START_TYPE:
                file_name = payload.decode()
                os.makedirs(args.outdir, exist_ok=True)
                recieved_file = open(os.path.join(args.outdir, file_name), "wb")
                print(f"[Reciever]: Recieving File: {file_name}")
                expected_sequence += 1

            #Chunk Loaded
            elif packet_type == DATA_TYPE:
                buffer[sequence_number] = payload
                print(f"[Reciever]: Buffering Packet #{sequence_number}")

                #Write All Consecutive Buffered Packets
                while expected_sequence in buffer:
                    recieved_file.write(buffer.pop(expected_sequence))
                    print(f"[Reciever]: Writing Packet #{expected_sequence}")
                    expected_sequence += 1

            #Ending File
            elif packet_type == END_TYPE:
                end_sequence = sequence_number
                print(f"[Reciever]: Ending Packet Recieved")

            #Acknowledge Reciept
            sock.sendto(create_packet(ACK_TYPE, 0, sequence_number, b""), addr)

            #Only End Once All Previous Packets Arrived
            if end_sequence is not None and expected_sequence == end_sequence:
                if recieved_file:
                    recieved_file.close()
                    recieved_file = None
                    print(f"[Reciever]: Ending File Upload")

                expected_sequence = 0
                buffer = {}
                end_sequence = None

        #Duplicate Packet
        elif sequence_number < expected_sequence:
            print(f"[Reciever]: ----Duplicate Packet Discarded")
            sock.sendto(create_packet(ACK_TYPE, 0, sequence_number, b""), addr)

        #Packet Outside Window
        else:
            print(f"[Reciever]: Packet #{sequence_number} Outside Window")
            
if __name__ == "__main__":
    main()
