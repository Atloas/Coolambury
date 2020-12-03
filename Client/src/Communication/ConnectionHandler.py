from PyQt5 import QtWidgets, QtCore, QtGui

from . import common
from . import msg_handler
import config
import messages
import socket
import threading
import logging


class ConnectionHandler:

    def __init__(self, switch_window):
        self.switch_window = switch_window
        self.connectedReceiverStatus = True
        self.server_config = config.Config()
        self.SERVER = self.server_config.SERVER
        self.PORT = self.server_config.PORT
        self.ADDR = (self.SERVER, self.PORT)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.ADDR)
        

        self.receiver_thread = threading.Thread(
            target=self.receive, args=(self.conn, self.server_config))
        self.receiver_thread.start()
        # raise ServerConnectionFailed(self.SERVER, self.PORT)

    def kill_receiver(self):
        self.connectedReceiverStatus = False

    def get_connected_receiver_status(self):
        return self.connectedReceiverStatus

    def receive(self, conn, server_config):
        while self.connectedReceiverStatus:
            received_msg = msg_handler.receive(conn, server_config)
            received_msg = received_msg[1] # get message body from tuple
            if received_msg:
                logging.debug(
                    "[RECEIVE MSG] {}".format(received_msg))
                if isinstance(received_msg, messages.CreateRoomResp) and received_msg.status == 'OK':
                    # self.serverOutputLabel.setText(str(received_msg))
                    self.switch_window.emit(received_msg.room_code, self)
                elif isinstance(received_msg, messages.NewChatMessage):
                    print(str(received_msg))
                    # self.serverOutputLabel.setText(str(received_msg))
                    # self.switch_window.emit(received_msg.room_code, self)

    def send_create_room_req(self):
        send_create_room_req_msg = messages.CreateRoomReq()
        send_create_room_req_msg.user_name = 'michalloska'
        send_create_room_req_msg.room_name = 'TestowyRoom'
        msg_handler.send(self.conn, send_create_room_req_msg,
                         self.server_config)

    def send_chat_msg_req(self, user_name, room_name, message):
        send_char_msg = messages.WriteChatReq()
        send_char_msg.user_name = user_name
        send_char_msg.room_code = room_name
        send_char_msg.message = message
        msg_handler.send(self.conn, send_char_msg,
                         self.server_config)


if __name__ == '__main__':
    pass
