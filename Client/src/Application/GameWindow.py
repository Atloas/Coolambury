from PyQt5 import QtCore, QtWidgets, QtGui
import logging


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    chat_message_signal = QtCore.pyqtSignal(str)
    scoreboard_update_signal = QtCore.pyqtSignal(str)
    key_pressed_signal = QtCore.pyqtSignal(QtCore.QEvent)

    def __init__(self, clientContext, connHandler):
        # TODO: Reset windows state on switch

        QtWidgets.QWidget.__init__(self)

        self.clientContext = clientContext
        self.connHandler = connHandler
        self.connHandler.chat_message_signal.connect(self.display_user_msg)
        self.connHandler.scoreboard_update_signal.connect(
            self.update_scoreboard)
        self.setWindowTitle("Coolambury [{}] {}".format(
            self.clientContext['username'],
            self.clientContext['roomCode']))

        # Drawing
        self.previousX = None
        self.previousY = None
        # TODO: Stores a history of pictures from past rounds. Add a copy of strokes here after a round is over.
        self.pictures = []
        self.strokes = []
        self.stroke = []

        # TODO: Before initializing game variables the window needs to know if it's a new game or if the user joined in progress

        # Game
        # Contains a list of all player names and their scores, ex. [["Atloas", 100], ["loska", 110]]
        # Player drawing order enforced by server?
        self.playerList = []
        # The currently painting person
        self.currentPainter = None
        # The hint text, modifiable on server request.
        # For the painter, should display the full word. Placeholder for now.
        self.hint = "____"

        # Window
        # self.key_pressed_signal.connect(self.on_key)

        # Drawing
        self.previousX = None
        self.previousY = None
        # TODO: Stores a history of pictures from past rounds. Add a copy of strokes here after a round is over.
        self.pictures = []
        self.strokes = []
        self.stroke = []

        # TODO: Before initializing game variables the window needs to know if it's a new game or if the user joined in progress

        # Game
        # Contains a list of all player names and their scores, ex. [["Atloas", 100], ["loska", 110]]
        # Player drawing order enforced by server?
        self.playerList = []
        # The currently painting person
        self.currentPainter = None
        # The hint text, modifiable on server request.
        # For the painter, should display the full word. Placeholder for now.
        self.hint = "____"

        # Window
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
        self.chat.append('GAME ROOM ID: {}\n'.format(
            self.clientContext['roomCode']))
        self.chat.setReadOnly(True)

        print(self.clientContext['roomCode'])
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

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for client exit")
        if self.connHandler.is_connection_receiver_connected():
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

        if self.previousX is None:
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

    def handleReceivedStroke(self, stroke):
        # TODO: Nothing actually receives data yet

        self.strokes.append(stroke.copy())

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        pen = painter.pen()
        pen.setColor(QtGui.QColor("black"))
        pen.setWidth(4)
        painter.begin(self.canvas)
        painter.setPen(pen)
        for i in range(len(stroke) - 1):
            painter.drawLine(stroke[i][0], stroke[i][1],
                             stroke[i+1][0], stroke[i+1][1])
        logging.debug("Received and drew stroke.")
        painter.end()
        self.update()

    def userJoined(self, username):
        self.playerList.append(username)
        # TODO: Add to scoreboard and update it.

        self.chat.ensureCursorVisible()

    def update_scoreboard(self, message):
        pass

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
