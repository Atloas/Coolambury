from PyQt5 import QtWidgets, QtCore, QtGui

from . import SocketMsgHandler
from Utils.PopUpWindow import PopUpWindow

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
            
            logging.debug(
                "[SOCKET RECEIVER] Received Message: {}".format(received_msg))
            self.dispatch_received_message(received_msg)

    def dispatch_received_message(self, received_msg):
        logging.debug(
            "[SOCKET RECEIVER] Received Message: {}".format(received_msg))
        message_dispatcher = {
            'CreateRoomResp': self.handle_CreateRoomResp,
            'JoinRoomResp': self.handle_JoinRoomResp,
            'NewChatMessage': self.handle_NewChatMessage
            # TODO: Implement on the server side:
            # 'ExitClientReq': self.handle_ExitClientReq(message)
        }
        return message_dispatcher.get(received_msg['msg_name'], self.handle_UnrecognizedMessage)(received_msg)

    def handle_CreateRoomResp(self, received_msg):
        if received_msg['status'] == 'OK':
            self.switch_window.emit(received_msg['room_code'])
        else:
            PopUpWindow('Room could not be created!', 'ERROR')
            logging.debug(
                "[MESSAGE DISPATCHER] handling CreateRoomResp failed, STATUS NOK")
        logging.debug(
            "[MESSAGE DISPATCHER] handling CreateRoomResp Successful, STATUS OK")

    def handle_JoinRoomResp(self, received_msg):
        if received_msg['status'] == 'OK':
            self.switch_window.emit('Joining')
        else:
            PopUpWindow('Could not join to room!', 'ERROR')
            logging.debug(
                "[MESSAGE DISPATCHER] handling JoinRoomResp failed, STATUS NOK")
        logging.debug(
            "[MESSAGE DISPATCHER] handling JoinRoomResp Successful, STATUS OK")

    def handle_NewChatMessage(self, received_msg):
        logging.debug(
            "[MESSAGE DISPATCHER] handling NewChatMessage: {}".format(received_msg))
        self.chat_message_signal.emit("{}: {}".format(
            received_msg['author'], received_msg['message']))

    def handle_ExitClientReq(self, received_msg):
        # TODO: Implement on the server side:
        self.kill_receiver()
        self.chat_message_signal.emit("{} has left the game".format(
            received_msg['user_name']))
        logging.debug(
            "[MESSAGE DISPATCHER] handling ExitClientReq Successful, STATUS OK")

    def handle_UnrecognizedMessage(self, received_msg):
        logging.debug(
            "[MESSAGE DISPATCHER] No defined handler for message: {}".format(received_msg))

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

    def send_exit_client_req(self, user_name, room_code):
        notify_server_about_leaving = {
            'msg_name': 'ExitClientReq',
            'user_name': user_name,
            'room_code': room_code
        }
        SocketMsgHandler.send(
            self.conn, notify_server_about_leaving, self.server_config)


if __name__ == '__main__':
    pass
