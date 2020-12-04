from PyQt5 import QtWidgets, QtCore, QtGui
import socket
import threading
import logging
from Utils.PopUpWindow import PopUpWindow
import Common.config
from Communication import msg_handler, ConnectionHandler
from Communication.ConnectionHandler import ConnectionHandler


class ServerConnectionFailed(Exception):
    def __init__(self, server_ip, server_port, message="Server unreachable"):
        self.server_ip = server_ip
        self.server_port = server_port
        self.message = "Server at the address {}:{} unreachable".format(
            server_ip, server_port)
        super().__init__(self.message)


class StartWindow(QtWidgets.QWidget):
    def __init__(self, connHandler, clientContext):
        super().__init__()

        self.connHandler = connHandler
        self.clientContext = clientContext

        self.setMinimumSize(150, 100)
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
        self.createRoombutton.clicked.connect(
            self.delegate_room_creation_to_handler)
        self.killReceiverButton = QtWidgets.QPushButton(
            "Kill Receiver before leaving")
        self.killReceiverButton.clicked.connect(self.connHandler.kill_receiver)

        self.setLayout(self.vBox)
        self.vBox.addWidget(self.nicknameLabel)
        self.vBox.addWidget(self.nicknameField)
        self.vBox.addWidget(self.roomCodeLabel)
        self.vBox.addWidget(self.roomCodeField)
        self.vBox.addWidget(self.joinButton)
        self.vBox.addWidget(self.createRoombutton)
        self.vBox.addWidget(self.killReceiverButton)

    def validate_nickname(self):
        isNickNameValid = self.nicknameField.isModified()
        logging.debug(
            "[NICKNAME VALIDATION] Given nickname is valid: {}".format(isNickNameValid))
        if isNickNameValid:
            return True
        else:
            PopUpWindow(
                "Nickname not valid!", 'ERROR')
            return False

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

    # def closeEvent(self, event):
        # if self.connHandler.get_connected_receiver_status() == True:
        #     logging.debug(
        #         "[EXITING] Killing all threads and exiting the client window")
        # self.connHandler.kill_receiver()
        # self.connHandler.send_create_room_req()  # temporary
        # TODO: Add a Message notifying the Server about a user leaving (kills the thread)
        # notify_server_about_leaving = messages.ExitClientReq()
        # notify_server_about_leaving.user_name = 'TestUser'
        # msg_handler.send(
        #     self.conn, notify_server_about_leaving, self.server_config)

    def delegate_room_creation_to_handler(self):
        if self.validate_nickname():
            self.clientContext['username'] = self.nicknameField.text()
            self.connHandler.send_create_room_req(
                self.clientContext['username'])

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
