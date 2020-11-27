import socket
import threading
import logging

PORT = 5050
# PORT = 25845
HEADER_LEN = 64

 # linode
# SERVER = '149.156.109.1' # taurus

FORMAT = 'utf-8'

DISCONNECT_MSG = '!DISCONNECT'

ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)

    send_length += b' ' * (HEADER_LEN - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

send("No czesc!!!")
send("Dziala to?")

send(DISCONNECT_MSG)
