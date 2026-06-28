import socket
import time
import argparse
import select
from support import DATA_TYPE, ACK_TYPE, START_TYPE, END_TYPE, HEADER_LENGTH, MAX_PAYLOAD_LENGTH, create_packet, unpack_packet, load_data

sock = None
retransmissions = 0
destination = None


"""
    Sends A Sequence Of Packets Using The Go Back N Approach

"""
def send_gbn(packets:dict, final_seq:int, window:int, timeout:float, max_attempts:int=20):
    global retransmissions

    base = 0                 
    next_sequence = 0             
    base_sent = None
    attempts = 0

    while base <= final_seq:

        #Fill Available Window
        while next_sequence < base + window and next_sequence <= final_seq:
            sock.sendto(packets[next_sequence], destination)
            print(f"[Sender]: Sent Packet #{next_sequence}  (base={base})")
            if base_sent is None:
                base_sent = time.time()
            next_sequence += 1

        #Determine Time Remaining On Base Timer
        remaining = timeout - (time.time() - base_sent)
        recieved_packet = None


        #Await Packet In Time Remaining
        if remaining > 0:
            try:
                sock.settimeout(remaining)
                recieved_packet, _ = sock.recvfrom(MAX_PAYLOAD_LENGTH+HEADER_LENGTH)
            except socket.timeout:
                pass

        #No Packet Recieved Within Timeout Period: Resend All
        if not recieved_packet:
            for window_seq in range(base, next_sequence):
                print(f"[Sender]: Resending Packet #{window_seq} (base={base})")
                sock.sendto(packets[window_seq], destination)
                retransmissions += 1
            base_sent = time.time()
            attempts += 1

        #Packet Recieved
        else:
            packet_type, _, recieved_ack, _ = unpack_packet(recieved_packet)

            #Previous ACK
            if recieved_ack < base:
                print(f"[Sender]: Recieved Previous ACK{recieved_ack}#")

            #Cumulative ACK In Window
            elif packet_type == ACK_TYPE:
                base = recieved_ack + 1
                attempts = 0
                base_sent = time.time()

        if attempts > max_attempts:
            raise Exception("Maxiumum Attempts Reached")

"""
Sends A File Or Specified Bytes Using Go Back N
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
        ap.add_argument("--window",  type=int,   default=10)
        args = ap.parse_args()

        #Create UDP Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        destination = (args.host, args.port)

        #Extract File Data Into Packets
        file_packets, file_name, file_size, total_packets = load_data(args.file, args.size)
        print(f"[Sender]: Sending {file_name} (Bytes:{file_size}, Packets:{total_packets} + 2, Window:{args.window})")

        #Builds Packets To Send
        packets = {0: create_packet(START_TYPE, 0, 0, file_name.encode())}
        
        for i, chunk in enumerate(file_packets):
            packets[i + 1] = create_packet(DATA_TYPE, i + 1, 0, chunk)
        
        final_seq = total_packets + 1
        packets[total_packets + 1] = create_packet(END_TYPE, final_seq, 0, b"")

        start_time = time.time()

        #Send Packets
        send_gbn(packets, final_seq, args.window, args.timeout)
        
        total_time = time.time() - start_time
        throughput = file_size / total_time
        print(f"""[Sender]: File Sent Successfully (Time:{total_time:.2f}s, Retransmissions:{retransmissions}, Throughput:{throughput:,.2f} bps)""")

    except Exception as e:
        print(f"[Sender]: ERROR {str(e)}")

    finally:
        if sock is not None:
            sock.close()
            print("[Sender]: Socket Closed")


if __name__ == "__main__":
    main()