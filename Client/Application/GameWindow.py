import logging
from enum import Enum

from PyQt5 import QtCore, QtWidgets, QtGui

from .DrawingHistoryWindow import DrawingHistoryWindow


class GameState(Enum):
    PREGAME = 0
    PROMPT_SELECTION = 1
    DRAWING = 2
    POSTGAME = 3


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    scoreboard_update_signal = QtCore.pyqtSignal(str)
    key_pressed_signal = QtCore.pyqtSignal(QtCore.QEvent)
    player_joined_signal = QtCore.pyqtSignal(dict)
    player_left_signal = QtCore.pyqtSignal(dict)
    start_signal = QtCore.pyqtSignal(dict)
    select_prompt_signal = QtCore.pyqtSignal(dict)
    stroke_signal = QtCore.pyqtSignal(dict)
    undo_signal = QtCore.pyqtSignal()
    clear_signal = QtCore.pyqtSignal()
    guess_correct_signal = QtCore.pyqtSignal(dict)
    chat_message_signal = QtCore.pyqtSignal(str)
    artist_change_signal = QtCore.pyqtSignal(dict)
    game_over_signal = QtCore.pyqtSignal(dict)

    def __init__(self, clientContext, connHandler):
        # TODO: Reset window's state on switch

        QtWidgets.QWidget.__init__(self)

        self.clientContext = clientContext
        self.connHandler = connHandler
        self.connHandler.chat_message_signal.connect(self.display_user_msg)
        self.connHandler.scoreboard_update_signal.connect(
            self.updateScoreboard)
        self.setWindowTitle("Coolambury [{}] {}".format(
            self.clientContext['username'],
            self.clientContext['roomCode']))

        # Game
        # Contains a dict of all player names and their scores, ex. {"Atloas": 100, "loska": 110}
        # Player drawing order enforced by server?
        self.gameState = None
        self.player = self.clientContext['username']
        self.owner = None  # TODO
        self.players = {}
        # The currently painting person
        self.artist = None
        # The hint text, modifiable on server request.
        # For the painter, should display the full word. Placeholder for now.
        self.hint = "____"

        # Drawing
        self.previousX = None
        self.previousY = None
        # TODO: Stores a history of pictures from past rounds. Add a copy of strokes here after a round is over.
        self.drawings = []
        self.strokes = []
        self.stroke = []

        # Window
        self.rootVBox = QtWidgets.QVBoxLayout()
        self.topHBox = QtWidgets.QHBoxLayout()
        self.bottomHBox = QtWidgets.QHBoxLayout()
        self.gameAndControlsVBox = QtWidgets.QVBoxLayout()
        self.controlsHBox = QtWidgets.QHBoxLayout()
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
        self.undoButton.clicked.connect(self.undoClicked)
        self.controlsHBox.addWidget(self.undoButton)

        self.clearButton = QtWidgets.QPushButton("Clear")
        self.clearButton.clicked.connect(self.clearClicked)
        self.controlsHBox.addWidget(self.clearButton)

        self.gameAndControlsVBox.addLayout(self.controlsHBox)

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

        self.bottomHBox.addLayout(self.gameAndControlsVBox)
        self.bottomHBox.addLayout(self.chatVBox)

        self.rootVBox.addLayout(self.topHBox)
        self.rootVBox.addLayout(self.bottomHBox)

        self.setLayout(self.rootVBox)

    def initialize_new_room(self):
        # Set room state to a fresh one with just the owner
        self.gameState = GameState.PREGAME
        self.owner = self.clientContext['username']
        self.players[self.owner] = 0
        self.hint = "PREGAME"
        self.previousX = None
        self.previousY = None
        self.drawings = []
        self.strokes = []
        self.stroke = []

        self.clear()
        self.updateScoreboard()

        self.display_chat_message("Type !start to start the game once there's at least two players in the room!")

    def initialize_joined_room(self, room_state):
        self.gameState = room_state['gameState']
        self.owner = room_state['owner']
        self.players = room_state['playerList']
        self.players[self.player] = 0
        self.hint = room_state['hint']
        self.strokes = room_state['strokes']
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

    def display_chat_message(self, message):
        # TODO: Have a separate "System message" chat message with different formatting to differentiate chat and information
        self.chat.insertPlainText("{}{}".format(message, "\n"))

    def display_user_msg(self, message):
        self.chatEntryLine.clear()
        self.chatEntryLine.setText('')
        self.chat.insertPlainText("{}{}".format(message, "\n"))

    def mouseMoveEvent(self, event):
        # TODO: Enable this
        # if self.artist != self.player:
        #     return

        x = event.x() - self.canvasContainer.x()
        y = event.y() - self.canvasContainer.y()

        if self.previousX is None:
            self.previousX = x
            self.previousY = y

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        painter.begin(self.canvas)
        painter.drawLine(self.previousX, self.previousY, x, y)
        # logging.debug("MouseMoveEvent at x: {}, y: {}".format(x, y))
        painter.end()
        self.update()

        self.previousX = x
        self.previousY = y

        self.stroke.append((x, y))

    def mouseReleaseEvent(self, event):
        # TODO: Enable this
        # if self.artist != self.player:
        #     return

        self.strokes.append(self.stroke.copy())
        self.previousX = None
        self.previousY = None

        # logging.debug(self.strokes)
        # TODO: send stroke data to server

        self.stroke = []

    def handlePlayerJoinedSignal(self, contents):
        self.display_chat_message("{} joined the room.".format(contents["player"]))
        self.players[contents.player] = 0
        self.updateScoreboard()

    def handlePlayerLeftSignal(self, contents):
        self.display_chat_message("{} left the room.".format(contents["player"]))
        del self.players[contents.player]
        self.updateScoreboard()
        # TODO: Handle all them edge cases.
        # TODO: What if the artist leaves, what if the owner leaves, what if the owner is left alone.

    def handleArtistChangeSignal(self, contents):
        # TODO: This drawings.append should be somewhere else, like in "guessing_over_signal", since now it won't fire on game over
        self.drawings.append(self.strokes.copy())
        self.display_chat_message("{} is now the artist.".format(contents["artist"]))
        self.artist = contents["artist"]
        self.gameState = GameState.PROMPT_SELECTION
        pass

    def handleSelectPromptSignal(self, contents):
        # TODO: Display a popup with 3 prompts given by the server to select from, message selection to server
        self.gameState = GameState.PROMPT_SELECTION
        pass

    def handlePromptSelectedSignal(self, contents):
        self.hint = len(contents["prompt"]) * "_"
        self.hints.setText(self.hint)
        self.clear()
        self.gameState = GameState.DRAWING
        pass

    def handleStrokeSignal(self, stroke):
        # TODO: Nothing actually receives data yet
        self.strokes.append(stroke.copy())

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        painter.begin(self.canvas)
        for i in range(len(stroke) - 1):
            painter.drawLine(stroke[i][0], stroke[i][1],
                             stroke[i + 1][0], stroke[i + 1][1])
        logging.debug("Received and drew stroke.")
        painter.end()
        self.update()

    def handleUndoSignal(self):
        self.undo()
        pass

    def handleClearSignal(self):
        self.clear()
        pass

    def handleGuessCorrectSignal(self, contents):
        self.display_chat_message("{} guessed right!".format(contents["player"]))
        self.players[contents["player"]] += contents["score_awarded"]
        self.players[self.artist] += contents["artist_score_awarded"]
        self.updateScoreboard()
        pass

    def handleGameOverSignal(self, contents):
        # TODO: Display window with all images drawn this round, allow user to save to disk?
        self.gameState = GameState.POSTGAME
        self.players = contents["final_scores"]
        self.updateScoreboard()
        tie = False
        topScore = 0
        winner = ""
        for player in self.players:
            if self.players[player] > topScore:
                topScore = self.players[player]
                winner = player
                tie = False
            elif self.players[player] == topScore:
                tie = True
        if tie:
            self.display_chat_message("It's a tie!")
        else:
            self.display_chat_message("{} has won!".format(winner))
        if self.drawings:
            DrawingHistoryWindow(self.drawings)
        self.drawings = []

    def undoClicked(self):
        self.undo()
        # TODO: Send undo message to server

    def clearClicked(self):
        self.stroke = []
        self.strokes = []
        self.clear()
        # TODO: Send clear message to server

    def redraw(self):
        self.clear()
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        painter.begin(self.canvas)
        for stroke in self.strokes:
            for i in range(len(stroke) - 1):
                painter.drawLine(stroke[i][0], stroke[i][1], stroke[i + 1][0], stroke[i + 1][1])
        painter.end()
        self.update()

    def undo(self):
        self.stroke = []
        if len(self.strokes) > 0:
            self.strokes.pop()
        self.redraw()

    def clear(self):
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        painter.begin(self.canvas)
        painter.eraseRect(0, 0, self.canvas.width(), self.canvas.height())
        painter.end()
        self.update()

    def configurePen(self, painter):
        pen = painter.pen()
        pen.setWidth(4)
        pen.setColor(QtGui.QColor("black"))
        painter.setPen(pen)

    def updateScoreboard(self):
        self.scoreboard.setRowCount(len(self.players))
        for i in range(len(self.players)):
            name = QtWidgets.QTableWidgetItem(self.players[i][0])
            score = QtWidgets.QTableWidgetItem(self.players[i][1])
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
        self.artist = data['painter']

    # TODO: move to connHandler if possible!
    def handle_message_send(self, message):
        self.connHandler.send_chat_msg_req(
            self.clientContext['username'], self.clientContext['roomCode'], message)

    def disconnect_clicked(self):
        # TODO: disconnect socket
        self.switch_window.emit()


if __name__ == '__main__':
    pass
