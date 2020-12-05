from PyQt5 import QtWidgets, QtCore, QtGui

from . import common
from . import msg_handler
import Common.config as config
import Common.messages as messages
from Utils import PopUpWindow

import socket
import threading
import logging


class ConnectionHandler(QtCore.QObject):
    chat_message_signal = QtCore.pyqtSignal(str)
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.connectedReceiverStatus = True
        self.server_config = config.Config()
        self.SERVER = self.server_config.SERVER
        self.PORT = self.server_config.PORT
        self.ADDR = (self.SERVER, self.PORT)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.ADDR)

        self.receiver_thread = threading.Thread(
            target=self.receive, args=(self.conn, self.server_config))
        self.receiver_thread.deamon = True
        self.receiver_thread.start()

    def kill_receiver(self):
        logging.debug(
            "[EXITING CONFIRMED] Killing all threads and exiting the client window")
        self.connectedReceiverStatus = False
        self.conn.close()
        self.receiver_thread.join()

    def get_connected_receiver_status(self):
        return self.connectedReceiverStatus

    def receive(self, conn, server_config):
        while self.connectedReceiverStatus:
            logging.debug("[SOCKET RECEIVER] Awaiting for incoming messages ...")
            received_msg_name, received_msg = msg_handler.receive(conn, server_config)
            if received_msg:
                logging.debug(
                    "[SOCKET RECEIVER] Received Message: {}".format(received_msg))
                if received_msg_name == 'CreateRoomResp':
                    if received_msg.status == 'OK':
                        self.switch_window.emit(received_msg.room_code)
                    else:
                        PopUpWindow('Room could not be created!', 'ERROR')
                elif received_msg_name == 'NewChatMessage':
                    self.chat_message_signal.emit("{}: {}".format(
                        received_msg.author, received_msg.message))
                elif received_msg_name == 'ExitClientReq':
                    kill_receiver()
                    self.chat_message_signal.emit("{} has left the game".format(
                        received_msg.user_name))

    def send_create_room_req(self, user_name):
        send_create_room_req_msg = messages.CreateRoomReq()
        send_create_room_req_msg.user_name = user_name
        send_create_room_req_msg.room_name = ''
        msg_handler.send(self.conn, send_create_room_req_msg,
                         self.server_config)

    def send_chat_msg_req(self, user_name, room_code, message):
        send_char_msg = messages.WriteChatReq()
        send_char_msg.user_name = user_name
        print("msg room_code = {}".format(room_code))
        send_char_msg.room_code = room_code

        send_char_msg.message = message
        msg_handler.send(self.conn, send_char_msg,
                         self.server_config)

    def send_exit_client_req(self, user_name):
        notify_server_about_leaving = messages.ExitClientReq()
        notify_server_about_leaving.user_name = user_name
        msg_handler.send(
            self.conn, notify_server_about_leaving, self.server_config)


if __name__ == '__main__':
    pass
