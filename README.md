### Stop And Wait Reciever
```
python3 receiver_stopwait.py --port 5005 --outdir reciever_files --loss 0.3

```


### Stop And Wait Sender
```
python3 sender_stopwait.py --host 127.0.0.1 --port 5005  --size 10000

python3 sender_stopwait.py --host 127.0.0.1 --port 5005 --file sender_files/CP372-S26.Assignment.2.docx

```



### GBN Reciever
```
python3 receiver_gbn.py --port 5005 --outdir reciever_files --loss 0.3

```


### GBN Sender
```
python3 sender_gbn.py --host 127.0.0.1 --port 5005  --size 10000 --window 5

python3 sender_gbn.py --host 127.0.0.1 --port 5005 --file sender_files/CP372-S26.Assignment.2.docx --window 5

```


