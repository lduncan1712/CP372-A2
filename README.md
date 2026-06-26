# CP372 - A2 - Group 30

## Stop and Wait
The Stop And Wait method is implemented using a reciever server (reciever_stopwait.py), and awaits and receives files from a sender client (sender_stopwait.py), sequentially started from the command line using the following format

### Reciever
|Argument | Description |
|---------|-------------|
| Host    | Reciever IP |
| Port    | Reciever Port |
| Loss    | Decimal Of Recieved Packets Randomly Dropped |
| Outdir  | Folder Path Where Sent Files Are Saved |
```
python3 receiver_stopwait.py --port 5005 --outdir reciever_files --loss 0.3
```

### Sender
|Argument | Description |
|---------|----------|
| Host    | Reciepient IP |
| Port    | Recipient Port |
| File    | Mode1: Optional File Name To Transfer
| Size    | Mode2: Optional Random File Size To Transfer | 
| Timeout | Time In Seconds Before Retransmission |
```
#Mode 1: Passing File
python3 sender_stopwait.py --host 127.0.0.1 --port 5005 --file sender_files/CP372-S26.Assignment.2.docx --timeout 1

#Mode 2: Random Data
python3 sender_stopwait.py --host 127.0.0.1 --port 5005  --size 10000 --timeout 1
```


## Go Back N
The Go Back N method is implemented using a reciever server (reciever_gbn.py), and awaits and receives files from a sender client (sender_gbn.py), sequentially started from the command line using the following format.

### Reciever
|Argument | Description |
|---------|-------------|
| Host    | Reciever IP |
| Port    | Reciever Port |
| Loss    | Decimal Of Recieved Packets Randomly Dropped |
| Outdir  | Folder Path Where Sent Files Are Saved |
```
python3 receiver_gbn.py --port 5005 --outdir reciever_files --loss 0.3
```

### Sender
|Argument | Description |
|---------|----------|
| Host    | Reciepient IP |
| Port    | Recipient Port |
| File    | Mode1: Optional File Name To Transfer
| Size    | Mode2: Optional Random File Size To Transfer | 
| Timeout | Time In Seconds Before Retransmission |
| Window  | Sender Transmission Window Size |
```
#Mode 1: File Name
python3 sender_gbn.py --host 127.0.0.1 --port 5005 --file sender_files/CP372-S26.Assignment.2.docx --window 5 --timeout 1

#Mode 2: Random Data
python3 sender_gbn.py --host 127.0.0.1 --port 5005  --size 10000 --window 5 --timeout 1
```


