from PyQt5 import QtWidgets, QtCore, QtGui
import socket
import threading
import logging
from Utils.PopUpWindow import PopUpWindow
from Communication import SocketMsgHandler, ConnectionHandler
from Communication.ConnectionHandler import ConnectionHandler


class StartWindow(QtWidgets.QWidget):
    def __init__(self, connHandler, clientContext):
        super().__init__()

        self.connHandler = connHandler
        self.clientContext = clientContext

        self.setMinimumSize(250, 100)
        self.setMaximumSize(350, 200)
        self.setWindowTitle("Coolambury")
        self.vBox = QtWidgets.QVBoxLayout()
        self.nicknameLabel = QtWidgets.QLabel('Enter your nickname:')
        self.nicknameField = QtWidgets.QLineEdit()
        self.nicknameField.maxLength = 15
        self.roomCodeLabel = QtWidgets.QLabel('Enter room code:')
        self.roomCodeField = QtWidgets.QLineEdit()
        self.roomCodeField.maxLength = 8
        self.joinButton = QtWidgets.QPushButton("Join room")
        self.joinButton.clicked.connect(self.delegate_room_join_to_handler)
        self.createRoombutton = QtWidgets.QPushButton(
            "Create Room")
        self.createRoombutton.clicked.connect(
            self.delegate_room_creation_to_handler)

        self.setLayout(self.vBox)
        self.vBox.addWidget(self.nicknameLabel)
        self.vBox.addWidget(self.nicknameField)
        self.vBox.addWidget(self.roomCodeLabel)
        self.vBox.addWidget(self.roomCodeField)
        self.vBox.addWidget(self.joinButton)
        self.vBox.addWidget(self.createRoombutton)

    def validate_nickname(self):
        isNickNameValid = not self.nicknameField.text() == ''
        logging.debug(
            "[NICKNAME VALIDATION] Given nickname is valid: {}".format(isNickNameValid))
        if isNickNameValid:
            return True
        PopUpWindow(
            "Nickname not valid!", 'ERROR')
        return False

    def validate_room_code(self):
        isRoomCodeValid = not self.roomCodeField.text() == ''
        logging.debug(
            "[ROOM CODE VALIDATION] Room code specified: {}".format(isRoomCodeValid))
        if isRoomCodeValid:
            return True
        PopUpWindow(
            "Room code not specified!", 'ERROR')
        return False

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for application exit")
        if self.connHandler.is_connection_receiver_connected() == True:
            self.connHandler.kill_receiver()

    def delegate_room_creation_to_handler(self):
        if self.validate_nickname():
            self.clientContext['username'] = self.nicknameField.text()
            self.connHandler.send_create_room_req(
                self.clientContext['username'])

    def delegate_room_join_to_handler(self):
        if self.validate_nickname() and self.validate_room_code():
            self.clientContext['username'] = self.nicknameField.text()
            self.clientContext['roomCode'] = self.roomCodeField.text()
            self.connHandler.send_join_room_req(
                self.clientContext['username'], self.clientContext['roomCode'])


if __name__ == '__main__':
    pass
