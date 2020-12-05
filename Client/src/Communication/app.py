import socket
import threading
import logging

import common
import config
import messages
import SocketMsgHandler

c_room_resp = messages.CreateRoomResp()

def receive(conn, config):
    global c_room_resp
    connected = True
    while connected:
        (name, received_msg) = SocketMsgHandler.receive(conn, config)
        if received_msg:
            if name == 'CreateRoomResp':
                c_room_resp = received_msg
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
    
    create_room_msg = messages.CreateRoomReq()

    create_room_msg.user_name = 'room_owner_user_hehe'
    create_room_msg.room_name = 'TestowyRoom'

    SocketMsgHandler.send(conn, create_room_msg, config)


    while True:
        mes = input()
        write_chat_req = messages.WriteChatReq()
        write_chat_req.user_name = create_room_msg.user_name
        write_chat_req.room_code = c_room_resp.room_code
        write_chat_req.message = mes
        SocketMsgHandler.send(conn, write_chat_req, config)


    receiver_thread.join()

