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

    #Await Packets
    while True:

        #Extract Packet
        packet, addr = sock.recvfrom(65535)
        packet_type, sequence_number, ack, payload = unpack_packet(packet)

        #Packet Loss (Drop Before Processing So No ACK Is Sent)
        if packet_type == DATA_TYPE and random.random() < args.loss:
            print("[Reciever]: ----Packet Lost Intentionally")
            continue

        #Correct Packet
        if sequence_number == expected_sequence:

            #Begin File
            if packet_type == START_TYPE:
                file_name = payload.decode()
                os.makedirs(args.outdir, exist_ok=True)
                recieved_file = open(os.path.join(args.outdir, file_name), "wb")
                print(f"[Reciever]: Recieving File: {file_name}")
                expected_sequence += 1

            #Chunk Loaded
            elif packet_type == DATA_TYPE:
                recieved_file.write(payload)
                print(f"[Reciever]: Acknowledging Packet #{sequence_number}")
                expected_sequence += 1

            #Ending File
            elif packet_type == END_TYPE:
                #Closing File
                if recieved_file:
                    recieved_file.close()
                    recieved_file = None
                    print(f"[Reciever]: Ending File Upload")

                #Preparing For Next File
                expected_sequence = 0
            sock.sendto(create_packet(ACK_TYPE, 0, sequence_number, b""), addr)

        #Duplicate, ACK Last Recieved (Expected - 1)
        else:
            print(f"[Reciever]: ACK{sequence_number} Out Of Order Or Duplicated")
            sock.sendto(create_packet(ACK_TYPE, 0, expected_sequence-1, b""), addr)


if __name__ == "__main__":
    main()