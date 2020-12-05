from PyQt5 import QtCore, QtWidgets, QtGui
import logging


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    chat_message_signal = QtCore.pyqtSignal(str)
    key_pressed_signal = QtCore.pyqtSignal(QtCore.QEvent)

    def __init__(self, clientContext, connHandler):
        QtWidgets.QWidget.__init__(self)

        self.clientContext = clientContext
        self.connHandler = connHandler
        self.connHandler.chat_message_signal.connect(self.display_user_msg)
        self.key_pressed_signal.connect(self.on_key)
        self.setWindowTitle("Coolambury: {}".format(
            self.clientContext['roomCode']))

        # TODO: Drawing
        self.vBox = QtWidgets.QVBoxLayout()
        self.topHBox = QtWidgets.QHBoxLayout()
        self.bottomHBox = QtWidgets.QHBoxLayout()
        self.chatVBox = QtWidgets.QVBoxLayout()
        self.chatBottomHBox = QtWidgets.QHBoxLayout()

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
        self.canvas = QtGui.QPixmap(400, 300)
        self.canvasContainer.setPixmap(self.canvas)
        self.bottomHBox.addWidget(self.canvasContainer)

        self.chat = QtWidgets.QTextEdit()
        self.chat.setReadOnly(True)

        self.chatEntryLine = QtWidgets.QLineEdit()
        self.chatEntryLine.setPlaceholderText("Have a guess!")
        self.chatEntryButton = QtWidgets.QPushButton("Send")
        # TODO: add Enter support/trigger

        self.chatEntryButton.clicked.connect(self.handle_message_send)

        self.chatBottomHBox.addWidget(self.chatEntryLine)
        self.chatBottomHBox.addWidget(self.chatEntryButton)

        self.chatVBox.addWidget(self.chat)
        self.chatVBox.addLayout(self.chatBottomHBox)

        self.bottomHBox.addLayout(self.chatVBox)

        self.vBox.addLayout(self.topHBox)
        self.vBox.addLayout(self.bottomHBox)

        self.setLayout(self.vBox)

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for client exit")
        if self.connHandler.get_connected_receiver_status() == True:
            # temporary:
            self.connHandler.kill_receiver()
            # TODO: implement ExitClientReq handling on the server:
            # self.connHandler.send_exit_client_req(self.clientContext['username'])
            # self.connHandler.receiver_thread.join()

    def keyPressEvent(self, event):
        pressedKey = event.key()
        if pressedKey == QtCore.Qt.Key_Enter or pressedKey == QtCore.Qt.Key_Return:
            if not self.isModified():
                self.handle_message_send()

    def keyPressEvent(self, event):
        super(GameWindow, self).keyPressEvent(event)
        self.key_pressed_signal.emit(event)

    def on_key(self, event):
        logging.debug(
            "[KEY PRESSED] {} was pressed".format(event.key()))
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.handle_message_send()

    def display_user_msg(self, message):
        self.chatEntryLine.clear()
        self.chatEntryLine.setText('')
        self.chat.insertPlainText("{}{}".format(message, "\n"))

    # TODO: move to connHandler if possible!
    def handle_message_send(self):
        if self.chatEntryLine.isModified():
            self.connHandler.send_chat_msg_req(
                self.clientContext['username'], self.clientContext['roomCode'], self.chatEntryLine.text())

    def disconnect_clicked(self):
        # TODO: disconnect socket
        self.switch_window.emit()


if __name__ == '__main__':
    pass
