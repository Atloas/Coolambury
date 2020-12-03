from PyQt5 import QtWidgets, QtCore, QtGui
import socket
import threading
import logging

from Communication import common, msg_handler, ConnectionHandler
from Communication.ConnectionHandler import ConnectionHandler
# from common:
import config
import messages

import traceback

class ServerConnectionFailed(Exception):
    def __init__(self, server_ip, server_port, message="Server unreachable"):
        self.server_ip = server_ip
        self.server_port = server_port
        self.message = "Server at the address {}:{} unreachable".format(
            server_ip, server_port)
        super().__init__(self.message)


class PopUpWindow(QtWidgets.QDialog):
    def __init__(self, message: str, type="WARNING"):
        super().__init__()
        self.setMinimumSize(200, 50)
        self.setWindowTitle(type)
        self.vBox = QtWidgets.QVBoxLayout()
        self.warningLabel = QtWidgets.QLabel(message)
        self.setLayout(self.vBox)
        self.vBox.addWidget(self.warningLabel)
        self.exec_()
        # icon = QtGui.QIcon()


class StartWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(str, ConnectionHandler)

    def __init__(self):
        super().__init__()

        try:
            self.connHandler = ConnectionHandler(self.switch_window)
        except:
            traceback.print_exc()
            logging.debug("[SOCKET CONNECTION] Connection to server failed")
            # self.connHandler.kill_receiver()
            w1 = PopUpWindow('Game server is unreachable!')
            exit()  # correct?

        self.setWindowTitle("Coolambury")

        self.vBox = QtWidgets.QVBoxLayout()
        self.nicknameLabel = QtWidgets.QLabel('Enter your nickname:')
        self.nicknameField = QtWidgets.QLineEdit()
        self.nicknameField.maxLength = 15
        self.roomCodeLabel = QtWidgets.QLabel('Enter room code:')
        self.roomCodeField = QtWidgets.QLineEdit()
        self.roomCodeField.maxLength = 4
        self.joinButton = QtWidgets.QPushButton("Join room")
        self.joinButton.clicked.connect(self.join_clicked)
        self.createRoombutton = QtWidgets.QPushButton(
            "Create Room")
        self.createRoombutton.clicked.connect(self.connHandler.send_create_room_req)
        self.serverOutputLabel = QtWidgets.QLabel('server output')

        self.setLayout(self.vBox)
        self.vBox.addWidget(self.nicknameLabel)
        self.vBox.addWidget(self.nicknameField)
        self.vBox.addWidget(self.roomCodeLabel)
        self.vBox.addWidget(self.roomCodeField)
        self.vBox.addWidget(self.joinButton)
        self.vBox.addWidget(self.createRoombutton)
        self.vBox.addWidget(self.serverOutputLabel)

    def validate_inputs(self):
        if True:  # self.lineEdit1.text and len(self.lineEdit2.text) == 4:
            return True
        else:
            return False

    def connect_to_room(self):
        # TODO
        return True

    def display_message(self, message):
        alert = QtWidgets.QMessageBox()
        alert.setText(message)
        alert.exec_()

    def closeEvent(self, event):
        if self.connHandler.get_connected_receiver_status() == True:
            logging.debug(
                "[EXITING] Killing all threads and exiting the client window")
            # self.connHandler.kill_receiver()
            # self.connHandler.send_create_room_req()  # temporary
        # TODO: Add a Message notifying the Server about a user leaving (kills the thread)
        # notify_server_about_leaving = messages.ExitClientReq()
        # notify_server_about_leaving.user_name = 'TestUser'
        # msg_handler.send(
        #     self.conn, notify_server_about_leaving, self.server_config)

    def join_clicked(self):
        if self.validate_inputs():
            if self.connect_to_room():
                roomNumber = self.roomCodeField.text()
                self.switch_window.emit(roomNumber)
            else:
                self.display_message("Could not connect to room!")
        else:
            self.display_message("invalid inputs!")


if __name__ == '__main__':
    pass
