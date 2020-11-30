import socket
import threading
import logging

import common
import config
import messages
import msg_handler


config = config.Config()

SERVER = config.SERVER
PORT = config.PORT

ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


create_room_msg = messages.CreateRoom()

create_room_msg.username = 'TestowyUser'
create_room_msg.roomname = 'TestowyRoom'

msg_handler.send(client, create_room_msg, config)

