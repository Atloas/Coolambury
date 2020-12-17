from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum
import logging


class GameState(Enum):
    PREGAME = 0
    PROMPT_SELECTION = 1
    DRAWING = 2
    POSTGAME = 3


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    chat_message_signal = QtCore.pyqtSignal(str)
    scoreboard_update_signal = QtCore.pyqtSignal(str)
    game_start_signal = QtCore.pyqtSignal(dict)

    def __init__(self, clientContext, connHandler):
        # TODO: Reset windows state on switch

        QtWidgets.QWidget.__init__(self)

        self.clientContext = clientContext
        self.connHandler = connHandler
        self.connHandler.chat_message_signal.connect(self.display_user_msg)
        self.connHandler.scoreboard_update_signal.connect(
            self.updateScoreboard)
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
        self.gameState = ""
        self.player = self.clientContext['username']
        self.owner = None  # TODO
        self.playerList = []
        # The currently painting person
        self.currentPainter = None
        # The hint text, modifiable on server request.
        # For the painter, should display the full word. Placeholder for now.
        self.hint = "____"

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

        self.hints = QtWidgets.QLabel("*HINTS*")  # TODO: Hints
        self.topHBox.addWidget(self.hints)

        self.scoreboard = QtWidgets.QTableWidget()
        self.scoreboard.setColumnCount(2)
        self.bottomHBox.addWidget(self.scoreboard)

        self.canvasContainer = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(400, 300)
        self.canvas.fill(QtGui.QColor("white"))
        self.canvasContainer.setPixmap(self.canvas)
        self.gameAndControlsVBox.addWidget(self.canvasContainer)

        self.undoButton = QtWidgets.QPushButton("Undo")
        self.clearButton.clicked.connect(self.undoClicked)
        self.controlsHBox.addWidget(self.undoButton)

        self.clearButton = QtWidgets.QPushButton("Clear")
        self.clearButton.clicked.connect(self.clearClicked)
        self.controlsHBox.addWidget(self.clearButton)

        self.chat = QtWidgets.QTextEdit()
        self.chat.append('GAME ROOM ID: {}\n'.format(
            self.clientContext['roomCode']))
        self.chat.setReadOnly(True)

        print(self.clientContext['roomCode'])
        self.chatEntryLine = QtWidgets.QLineEdit()
        self.chatEntryLine.setPlaceholderText("Have a guess!")
        self.chatEntryLine.returnPressed.connect(self.newChatMessage)

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

    def initializeNewRoom(self):
        # Set room state to a fresh one with just the owner
        self.gameState = GameState.PREGAME
        self.owner = self.clientContext['username']
        self.playerList.append([self.owner, 0])
        self.hint = "PREGAME"
        self.previousX = None
        self.previousY = None
        self.pictures = []
        self.strokes = []
        self.stroke = []

        self.clear()
        self.updateScoreboard()

        self.displayChatMessage("Type !start to start the game once there's at least two players in the room!")

    def initializeJoinedRoom(self, roomState):
        self.gameState = roomState['gameState']
        self.owner = roomState['owner']
        self.playerList.append(roomState['playerList'])
        self.hint = roomState['hint']
        self.strokes = roomState['strokes']
        # Pictures, stroke, previousX, previousY don't need to be initialized here?

        self.redraw()
        self.updateScoreboard()

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for client exit")
        if self.connHandler.is_connection_receiver_connected():
            # temporary:
            self.connHandler.kill_receiver()
            # TODO: implement ExitClientReq handling on the server:
            # self.connHandler.send_exit_client_req(self.clientContext['username'])
            # self.connHandler.receiver_thread.join()

    def displayChatMessage(self, message):
        self.chat.insertPlainText("{}{}".format(message, "\n"))

    def display_user_msg(self, message):
        self.chatEntryLine.clear()
        self.chatEntryLine.setText('')
        self.chat.insertPlainText("{}{}".format(message, "\n"))

    def mouseMoveEvent(self, e):
        # TODO: Enable this
        # if self.currentPainter != self.player:
        #     return

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
        # logging.debug("MouseMoveEvent at x: {}, y: {}".format(x, y))
        painter.end()
        self.update()

        self.previousX = x
        self.previousY = y

        self.stroke.append((x, y))

    def mouseReleaseEvent(self, e):
        # TODO: Enable this
        # if self.currentPainter != self.player:
        #     return

        self.strokes.append(self.stroke.copy())
        self.previousX = None
        self.previousY = None

        # logging.debug(self.strokes)
        # TODO: send stroke data to server

        self.stroke = []

    def handleReceivedStroke(self, stroke):
        # TODO: Nothing actually receives data yet
        self.strokes.append(stroke.copy())

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        pen = self.configurePen(painter)
        painter.setPen(pen)
        painter.begin(self.canvas)
        for i in range(len(stroke) - 1):
            painter.drawLine(stroke[i][0], stroke[i][1], stroke[i+1][0], stroke[i+1][1])
        logging.debug("Received and drew stroke.")
        painter.end()
        self.update()

    def undoClicked(self):
        logging.debug("Undo")
        self.stroke = []
        if len(self.strokes) > 0:
            self.strokes.pop()
        self.redraw()
        # TODO: Send undo message to server

    def clearClicked(self):
        logging.debug("Clear")
        self.stroke = []
        self.strokes = []
        self.clear()
        # TODO: Send clear message to server

    def redraw(self):
        logging.debug("Redraw")
        self.clear()
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        pen = self.configurePen(painter)
        painter.begin(self.canvas)
        painter.setPen(pen)
        for stroke in self.strokes:
            for i in range(len(stroke) - 1):
                painter.drawLine(stroke[i][0], stroke[i][1], stroke[i + 1][0], stroke[i + 1][1])
        painter.end()
        self.update()

    def clear(self):
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        painter.begin(self.canvas)
        painter.eraseRect(0, 0, self.canvas.width(), self.canvas.height())
        painter.end()

    def userJoined(self, username):
        self.playerList.append([username, 0])
        self.updateScoreboard()

    def updateScoreboard(self):
        self.scoreboard.setRowCount(len(self.playerList))
        for i in range(len(self.playerList)):
            name = QtWidgets.QTableWidgetItem(self.playerList[i][0])
            score = QtWidgets.QTableWidgetItem(self.playerList[i][1])
            self.scoreboard.setItem(i, 0, name)
            self.scoreboard.setItem(i, 1, score)

    def newChatMessage(self):
        message = self.chatEntryLine.text()
        if message != "":
            if message.startswith("!"):
                if message == "!start" and self.player == self.owner:
                    pass
                    # TODO: send "start_game_message"
            else:
                self.handle_message_send(message)

    def startMessage(self, data):
        self.currentPainter = data['painter']


    # TODO: move to connHandler if possible!
    def handle_message_send(self, message):
        self.connHandler.send_chat_msg_req(
            self.clientContext['username'], self.clientContext['roomCode'], message)

    def disconnect_clicked(self):
        # TODO: disconnect socket
        self.switch_window.emit()


if __name__ == '__main__':
    pass
