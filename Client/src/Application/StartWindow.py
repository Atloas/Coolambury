from PyQt5 import QtWidgets, QtCore, QtGui
import socket
import threading
import logging

from Communication import common, msg_handler
# from common:
import config, messages


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
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Socket initialization
        self.connectedReceiverStatus = True
        self.server_config = config.Config()
        self.SERVER = self.server_config.SERVER
        self.PORT = self.server_config.PORT
        self.ADDR = (self.SERVER, self.PORT)
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect(self.ADDR)
            self.receiver_thread = threading.Thread(
                target=self.receive, args=(self.conn, self.server_config))
            self.receiver_thread.start()
        except:
            logging.debug("[SOCKET CONNECTION] Connection to server failed")
            self.connectedReceiverStatus = False
            w1 = PopUpWindow('Game server is unreachable!')
            raise ServerConnectionFailed(self.SERVER, self.PORT)

        QtWidgets.QWidget.__init__(self)
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
            "Send a test Msg To Server :))))")
        self.createRoombutton.clicked.connect(self.send_create_room_req)
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
        if self.connectedReceiverStatus == True:
            logging.debug(
                "[EXITING] Killing all threads and exiting the client window")
            self.kill_receiver()
            self.send_create_room_req() # temporary
        # TODO: Add a Message notifying the Server about a user leaving (kills the thread)
        # notify_server_about_leaving = messages.ExitClientReq()
        # notify_server_about_leaving.user_name = 'TestUser'
        # msg_handler.send(
        #     self.conn, notify_server_about_leaving, self.server_config)

    def receive(self, conn, server_config):
        while self.connectedReceiverStatus:
            received_msg = msg_handler.receive(conn, server_config)
            if received_msg:
                print(received_msg)  # TODO jakis handler trzeba sobie zrobic
                self.serverOutputLabel.setText(received_msg.__str__())

    def kill_receiver(self):
        self.connectedReceiverStatus = False

    def send_create_room_req(self):
        send_create_room_req_msg = messages.CreateRoomReq()
        send_create_room_req_msg.user_name = 'TestowyUser'
        send_create_room_req_msg.room_name = 'TestowyRoom'
        msg_handler.send(self.conn, send_create_room_req_msg, self.server_config)

    def join_clicked(self):
        if self.validate_inputs():
            if self.connect_to_room():
                roomNumber = self.roomCodeField.text()
                self.switch_window.emit(roomNumber)
            else:
                self.display_message("Could not connect to room!")
        else:
            self.display_message("invalid inputs!")
