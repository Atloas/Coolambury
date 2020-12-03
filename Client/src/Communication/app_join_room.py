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
        (name, received_msg) = msg_handler.receive(conn, config)
        if received_msg:
            if name == 'NewChatMessage':
                print('{} : {}'.format(received_msg.author, received_msg.message))
            else:
                print(received_msg) # TODO jakis handler trzeba sobie zrobic 

config = config.Config()
SERVER = config.SERVER
PORT = config.PORT

ADDR = (SERVER, PORT)
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(ADDR)

receiver_thread = threading.Thread(target=receive, args=(conn, config))
receiver_thread.start()

if __name__ == "__main__":
    
    join_room_msg = messages.JoinRoomReq()

    join_room_msg.user_name = 'jakis_nick_inny'
    join_room_msg.room_code = 'eqnwnqpj'

    msg_handler.send(conn, join_room_msg, config)

    while True:
        mes = input()
        write_chat_req = messages.WriteChatReq()
        write_chat_req.user_name = join_room_msg.user_name
        write_chat_req.room_code = join_room_msg.room_code
        write_chat_req.message = mes
        msg_handler.send(conn, write_chat_req, config)


    receiver_thread.join()

