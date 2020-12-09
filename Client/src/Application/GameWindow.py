from PyQt5 import QtCore, QtWidgets, QtGui
import logging


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    chat_message_signal = QtCore.pyqtSignal(str)
    key_pressed_signal = QtCore.pyqtSignal(QtCore.QEvent)

    def __init__(self, clientContext, connHandler):
        # TODO: Reset windows state on switch

        QtWidgets.QWidget.__init__(self)

        self.clientContext = clientContext
        self.connHandler = connHandler
        self.connHandler.chat_message_signal.connect(self.display_user_msg)
        self.setWindowTitle("Coolambury: {}".format(
            self.clientContext['roomCode']))

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

        self.hints = QtWidgets.QLabel("*HINTS*")   # TODO: Hints
        self.topHBox.addWidget(self.hints)

        self.scoreboard = QtWidgets.QTableView()
        self.bottomHBox.addWidget(self.scoreboard)

        self.canvasContainer = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(400, 300)
        self.canvas.fill(QtGui.QColor("white"))
        self.canvasContainer.setPixmap(self.canvas)
        self.bottomHBox.addWidget(self.canvasContainer)

        self.chat = QtWidgets.QTextEdit()
        self.chat.setReadOnly(True)

        self.chatEntryLine = QtWidgets.QLineEdit()
        self.chatEntryLine.setPlaceholderText("Have a guess!")
        self.chatEntryLine.returnPressed.connect(self.handle_message_send)

        self.chatEntryButton = QtWidgets.QPushButton("Send")
        self.chatEntryButton.clicked.connect(self.handle_message_send)

        self.chatBottomHBox.addWidget(self.chatEntryLine)
        self.chatBottomHBox.addWidget(self.chatEntryButton)

        self.chatVBox.addWidget(self.chat)
        self.chatVBox.addLayout(self.chatBottomHBox)

        self.bottomHBox.addLayout(self.chatVBox)

        self.vBox.addLayout(self.topHBox)
        self.vBox.addLayout(self.bottomHBox)

        self.setLayout(self.vBox)

        self.previousX = None
        self.previousY = None
        self.strokes = []
        self.stroke = []

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for client exit")
        if self.connHandler.get_connected_receiver_status() == True:
            # temporary:
            self.connHandler.kill_receiver()
            # TODO: implement ExitClientReq handling on the server:
            # self.connHandler.send_exit_client_req(self.clientContext['username'])
            # self.connHandler.receiver_thread.join()

    def display_user_msg(self, message):
        self.chatEntryLine.clear()
        self.chatEntryLine.setText('')
        self.chat.insertPlainText("{}{}".format(message, "\n"))

    def mouseMoveEvent(self, e):
        x = e.x() - self.canvasContainer.x()
        y = e.y() - self.canvasContainer.y()

        if self.previousX == None:
            self.previousX = x
            self.previousY = y

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        pen = painter.pen()
        pen.setColor(QtGui.QColor("black"))
        pen.setWidth(4)
        painter.begin(self.canvas)
        painter.setPen(pen)
        painter.drawLine(self.previousX, self.previousY, x, y)
        logging.debug("MouseMoveEvent at x: {}, y: {}".format(x, y))
        painter.end()
        self.update()

        self.previousX = x
        self.previousY = y

        self.stroke.append((x, y))

    def mouseReleaseEvent(self, e):
        self.strokes.append(self.stroke.copy())
        self.previousX = None
        self.previousY = None

        logging.debug(self.strokes)

        # TODO: send stroke data to server

        self.stroke = []

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
