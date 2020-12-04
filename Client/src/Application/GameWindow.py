from PyQt5 import QtCore, QtWidgets, QtGui


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    chat_message_signal = QtCore.pyqtSignal(str)

    def __init__(self, roomCode, connHandler):
        QtWidgets.QWidget.__init__(self)
        self.roomCode = roomCode
        self.connHandler = connHandler
        
        self.setWindowTitle("Coolambury: {}".format(self.roomCode))

        # TODO: Drawing
        self.vBox = QtWidgets.QVBoxLayout()

        self.topHBox = QtWidgets.QHBoxLayout()

        self.bottomHBox = QtWidgets.QHBoxLayout()

        self.chatVBox = QtWidgets.QVBoxLayout()

        self.chatBottomHBox = QtWidgets.QHBoxLayout()

        self.disconnectButton = QtWidgets.QPushButton("Disconnect")
        self.disconnectButton.clicked.connect(self.disconnect_clicked)
        self.topHBox.addWidget(self.disconnectButton)

        self.hints = QtWidgets.QLabel("*HINTS*")   # TODO
        self.topHBox.addWidget(self.hints)

        self.scoreboard = QtWidgets.QTableView()
        self.bottomHBox.addWidget(self.scoreboard)

        self.canvasContainer = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)
        self.canvasContainer.setPixmap(canvas)
        self.bottomHBox.addWidget(self.canvasContainer)

        self.chat = QtWidgets.QTextEdit()

        self.chatEntryLine = QtWidgets.QLineEdit()
        self.chatEntryButton = QtWidgets.QPushButton("Send")
        # self.chatEntryButton.clicked.connect(self.connHandler.send_create_room_req)
        self.chatEntryButton.clicked.connect(self.handle_message_send)

        self.chatBottomHBox.addWidget(self.chatEntryLine)
        self.chatBottomHBox.addWidget(self.chatEntryButton)

        self.chatVBox.addWidget(self.chat)
        self.chatVBox.addLayout(self.chatBottomHBox)

        self.bottomHBox.addLayout(self.chatVBox)

        self.vBox.addLayout(self.topHBox)
        self.vBox.addLayout(self.bottomHBox)

        self.setLayout(self.vBox)

    def display_user_msg(self, message):
        self.chat.setText(message)

    def handle_message_send(self):
        self.connHandler.send_chat_msg_req(
            'michalloska', self.roomCode, '***** ***')

    def disconnect_clicked(self):
        # TODO: disconnect socket
        self.switch_window.emit()


if __name__ == '__main__':
    pass
