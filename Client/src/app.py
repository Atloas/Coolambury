import socket
import threading
import logging

import common
import config
import messages
import msg_handler

def receive(conn, config):
    connected = True
    while connected:
        received_msg = msg_handler.receive(conn, config)
        if received_msg:
            print(received_msg) # TODO jakis handler trzeba sobie zrobic 


config = config.Config()
SERVER = config.SERVER
PORT = config.PORT

ADDR = (SERVER, PORT)
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(ADDR)

receiver_thread = threading.Thread(target=receive, args=(conn, config))
receiver_thread.start()

create_room_msg = messages.CreateRoomReq()

create_room_msg.username = 'TestowyUser'
create_room_msg.roomname = 'TestowyRoom'

msg_handler.send(conn, create_room_msg, config)

receiver_thread.join()

