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
    print(f"[Receiver] Awaiting Packets From {args.host}:{args.port}  (Loss:{args.loss})")

    #Variables
    expected_sequence = 0
    recieved_file = None
    file_name = None


    #Await Packets
    while True:

        #Extract Packet
        packet, addr = sock.recvfrom(65535)
        packet_type, sequence_number, ack, payload = unpack_packet(packet)

        #Packet Loss
        if packet_type == DATA_TYPE and random.random() < args.loss:
            print("[Reciever]: ----Packet Lost Intentionally")
            continue

        #Expected Sequence Number
        if sequence_number == expected_sequence:

            #Begin File
            if packet_type == START_TYPE:
                file_name = payload.decode()
                os.makedirs(args.outdir, exist_ok=True)
                expected_sequence += 1
                recieved_file = open(os.path.join(args.outdir, file_name), "wb")
                print(f"[Reciever]: Recieving File: {file_name}")

            #Chunk Loaded
            elif packet_type == DATA_TYPE:
                recieved_file.write(payload)
                expected_sequence += 1
                print(f"[Reciever]: Acknowledging Packet #{sequence_number}")
                
            #Ending File
            elif packet_type == END_TYPE:

                #End File Upload
                if recieved_file:
                    recieved_file.close()
                    print(f"[Reciever]: Ending File Upload")

                #Prepare For Next File Upload
                expected_sequence = 0

            #Acknowledge Reciept
            sock.sendto(create_packet(ACK_TYPE, 0, sequence_number, b""), addr)   

        #Duplicate Sequence
        elif sequence_number < expected_sequence:
            print(f"[Reciever]: ----Duplicate Packet Discarded")
            sock.sendto(create_packet(ACK_TYPE, 0, sequence_number, b""), addr)

if __name__ == "__main__":
    main()