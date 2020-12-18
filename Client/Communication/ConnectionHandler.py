from PyQt5 import QtWidgets, QtCore, QtGui

from . import SocketMsgHandler
from Utils import PopUpWindow

import socket
import threading
import logging
import json
import sys


class ConnectionHandler(QtCore.QObject):
    chat_message_signal = QtCore.pyqtSignal(str)
    scoreboard_update_signal = QtCore.pyqtSignal(str)
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.connectedReceiverStatus = True

        self.server_config = self._load_config_file()
        self.SERVER = self.server_config['SERVER']
        self.PORT = self.server_config['PORT']
        self.ADDR = (self.SERVER, self.PORT)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.ADDR)

        self.receiver_thread = threading.Thread(
            target=self.receive, args=(self.conn, self.server_config))
        self.receiver_thread.deamon = True
        self.receiver_thread.start()

    def kill_receiver(self):
        try:
            self.connectedReceiverStatus = False
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            self.receiver_thread.join()
        except:
            logging.debug(
                "[SOCKET RECEIVER] Unsuccessful socket shutdown!")
        logging.debug(
            '[EXITING CONFIRMED] Killing all threads and exiting the client window')

    def _load_config_file(self):
        try:
            config_path = sys.argv[1]
            with open(config_path, 'r') as config_file:
                return json.load(config_file)
        except:
            logging.error(
                '[LOADING CONFIG FILE] Error occured when loading configuration file!')
            exit()

    def is_connection_receiver_connected(self):
        return self.connectedReceiverStatus

    def receive(self, conn, server_config):
        while self.connectedReceiverStatus:
            logging.debug(
                "[SOCKET RECEIVER] Awaiting for incoming messages ...")
            received_msg_name = None
            received_msg = None
            try:
                received_msg_name, received_msg = SocketMsgHandler.receive(
                    conn, server_config)
            except:
                logging.debug(
                    "[SOCKET RECEIVER] Shutting down and closing socket connection")
            if received_msg:
                logging.debug(
                    "[SOCKET RECEIVER] Received Message: {}".format(received_msg))
                if received_msg_name == 'CreateRoomResp':
                    if received_msg['status'] == 'OK':
                        self.switch_window.emit(received_msg['room_code'])
                    else:
                        PopUpWindow('Room could not be created!', 'ERROR')
                if received_msg_name == 'JoinRoomResp':
                    if received_msg['status'] == 'OK':
                        self.switch_window.emit('Joining')
                elif received_msg_name == 'NewChatMessage':
                    self.chat_message_signal.emit("{}: {}".format(
                        received_msg['author'], received_msg['message']))
                elif received_msg_name == 'ExitClientReq':
                    self.kill_receiver()
                    self.chat_message_signal.emit("{} has left the game".format(
                        received_msg.user_name))

    def send_create_room_req(self, user_name):
        send_create_room_req_msg = {
            'msg_name': 'CreateRoomReq',
            'user_name': user_name
        }
        SocketMsgHandler.send(self.conn, send_create_room_req_msg,
                              self.server_config)

    def send_join_room_req(self, user_name, room_code):
        send_join_room_req_msg = {
            'msg_name': 'JoinRoomReq',
            'user_name': user_name,
            'room_code': room_code
        }

        SocketMsgHandler.send(self.conn, send_join_room_req_msg,
                              self.server_config)

    def send_chat_msg_req(self, user_name, room_code, message):
        send_char_msg = {
            'msg_name': 'WriteChatReq',
            'user_name': user_name,
            'room_code': room_code,
            'message': message
        }
        SocketMsgHandler.send(self.conn, send_char_msg,
                              self.server_config)

    def send_exit_client_req(self, user_name): 
        notify_server_about_leaving = messages.ExitClientReq()
        notify_server_about_leaving.user_name = user_name
        SocketMsgHandler.send(
            self.conn, notify_server_about_leaving, self.server_config)


if __name__ == '__main__':
    pass
