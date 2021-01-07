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

        self.setWindowTitle("Coolambury")

        self.rootVBox = QtWidgets.QVBoxLayout()

        self.nicknameLabel = QtWidgets.QLabel('Enter your nickname:')
        self.rootVBox.addWidget(self.nicknameLabel)

        self.nicknameField = QtWidgets.QLineEdit()
        self.nicknameField.maxLength = 15
        self.rootVBox.addWidget(self.nicknameField)

        self.roomCodeLabel = QtWidgets.QLabel('Enter room code:')
        self.rootVBox.addWidget(self.roomCodeLabel)

        self.roomCodeField = QtWidgets.QLineEdit()
        self.roomCodeField.maxLength = 8
        self.rootVBox.addWidget(self.roomCodeField)

        self.joinButton = QtWidgets.QPushButton("Join room")
        self.joinButton.clicked.connect(self.delegate_room_join_to_handler)
        self.rootVBox.addWidget(self.joinButton)

        self.createRoomButton = QtWidgets.QPushButton(
            "Create Room")
        self.createRoomButton.clicked.connect(
            self.delegate_room_creation_to_handler)
        self.rootVBox.addWidget(self.createRoomButton)

        self.setLayout(self.rootVBox)

        #self.setFixedSize(self.size())

    # TODO: Add validation for special characters!
    def validate_nickname(self):
        isNickNameValid = not self.nicknameField.text() == ''
        logging.debug(
            "[NICKNAME VALIDATION] Given nickname is valid: {}".format(isNickNameValid))
        if isNickNameValid:
            return True
        return False

    def validate_room_code(self):
        isRoomCodeValid = not self.roomCodeField.text() == ''
        isRoomCodeValid = len(self.roomCodeField.text()) == 8

        logging.debug(
            "[ROOM CODE VALIDATION] Room code specified: {}".format(isRoomCodeValid))
        if isRoomCodeValid:
            return True
        return False

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for application exit")
        if self.connHandler.is_connection_receiver_connected():
            self.connHandler.send_socket_disconnect_req()
            self.connHandler.kill_receiver()

    def delegate_room_creation_to_handler(self):
        if self.validate_nickname():
            self.clientContext['username'] = self.nicknameField.text()
            self.connHandler.send_create_room_req(
                self.clientContext['username'])
        else:
            PopUpWindow("Nickname not valid!", 'ERROR')

    def delegate_room_join_to_handler(self):
        is_nickname_valid = self.validate_nickname()
        is_room_code_valid = self.validate_room_code()
        if is_nickname_valid and is_room_code_valid:
            self.clientContext['username'] = self.nicknameField.text()
            self.clientContext['roomCode'] = self.roomCodeField.text()
            self.connHandler.send_join_room_req(
                self.clientContext['username'], self.clientContext['roomCode'])
        elif (not is_nickname_valid):
            PopUpWindow("Nickname not valid!", 'ERROR')
        elif (not is_room_code_valid):
            PopUpWindow("Room code not specified!", 'ERROR')


if __name__ == '__main__':
    pass
