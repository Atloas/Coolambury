import logging
from enum import Enum

from PyQt5 import QtCore, QtWidgets, QtGui

from .DrawingHistoryWindow import DrawingHistoryWindow
from Utils.PopUpWindow import PopUpWindow
from enum import Enum
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets, QtGui
from .DrawingHistoryWindow import DrawingHistoryWindow


class GameState(Enum):
    PREGAME = 0
    WORD_SELECTION = 1
    DRAWING = 2
    POSTGAME = 3

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
    prompt_selected_signal = QtCore.pyqtSignal(dict)
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
        self.connHandler.chat_message_signal.connect(self.display_user_message)
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
        self.artist = None
        # The hint text, modifiable on server request.
        # For the painter, should display the full word. Placeholder for now.
        self.hint = "____"

        # Drawing
        self.previousX = None
        self.previousY = None
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
        self.disconnectButton.setMaximumSize(100, 50)
        self.disconnectButton.clicked.connect(self.disconnect_clicked)
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.setMaximumSize(100, 50)
        self.startButton.clicked.connect(self.start_clicked)
        self.topHBox.addWidget(self.disconnectButton)
        self.topHBox.addWidget(self.startButton)

        self.hints = QtWidgets.QLabel("*HINTS*")  # TODO: Hints
        self.topHBox.addWidget(self.hints)

        self.scoreboard = QtWidgets.QTableWidget()
        self.scoreboard.setColumnCount(2)
        self.bottomHBox.addWidget(self.scoreboard)

        self.canvasContainer = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(400, 400)
        self.canvas.fill(QtGui.QColor("white"))
        self.canvasContainer.setPixmap(self.canvas)
        self.gameAndControlsVBox.addWidget(self.canvasContainer)

        self.undoButton = QtWidgets.QPushButton("Undo")
        self.undoButton.setDisabled(True)
        self.undoButton.clicked.connect(self.undoClicked)
        self.controlsHBox.addWidget(self.undoButton)

        self.clearButton = QtWidgets.QPushButton("Clear")
        self.clearButton.setDisabled(True)
        self.clearButton.clicked.connect(self.clearClicked)
        self.controlsHBox.addWidget(self.clearButton)

        self.gameAndControlsVBox.addLayout(self.controlsHBox)

        self.chat = QtWidgets.QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.append("GAME ROOM ID: {}".format(
            self.clientContext['roomCode']))

        self.chatEntryLine = QtWidgets.QLineEdit()
        self.chatEntryLine.setPlaceholderText("Have a guess!")
        self.chatEntryLine.returnPressed.connect(self.newChatMessage)

        self.chatEntryButton = QtWidgets.QPushButton("Send")
        self.chatEntryButton.clicked.connect(self.newChatMessage)

        self.chatBottomHBox.addWidget(self.chatEntryLine)
        self.chatBottomHBox.addWidget(self.chatEntryButton)

        self.chatVBox.addWidget(self.chat)
        self.chatVBox.addLayout(self.chatBottomHBox)

        self.bottomHBox.addLayout(self.gameAndControlsVBox)
        self.bottomHBox.addLayout(self.chatVBox)

        self.rootVBox.addLayout(self.topHBox)
        self.rootVBox.addLayout(self.bottomHBox)

        self.setLayout(self.rootVBox)

        self.connectSignals()

    def connectSignals(self):
        # TODO: Test?
        self.player_joined_signal.connect(self.handlePlayerJoinedSignal)
        self.player_left_signal.connect(self.handlePlayerLeftSignal)
        self.start_signal.connect(self.handleStartSignal)
        self.select_prompt_signal.connect(self.handleSelectPromptSignal)
        self.prompt_selected_signal.connect(self.handlePromptSelectedSignal)
        self.stroke_signal.connect(self.handleStrokeSignal)
        self.undo_signal.connect(self.handleUndoSignal)
        self.clear_signal.connect(self.handleClearSignal)
        self.guess_correct_signal.connect(self.handleGuessCorrectSignal)
        self.artist_change_signal.connect(self.handleArtistChangeSignal)
        self.game_over_signal.connect(self.handleGameOverSignal)

    # TODO: Swap players for contents = {"owner": "a", "players": ["a", "b", "c"]}
    def initialize_room(self, players):
        # Set room state to a fresh one with just the owner
        self.gameState = GameState.PREGAME
        # self.owner = contents['owner']
        # players = contents['players']
        self.players = {}
        for player in players:
            self.players[player] = 0
        self.hint = "PREGAME"
        self.previousX = None
        self.previousY = None
        self.drawings = []
        self.strokes = []
        self.stroke = []

        self.clear()
        self.updateScoreboard()

        if self.player == self.owner:

            self.display_system_message(
                "Type !start to start the game once there's at least two players in the room!")

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for client exit")
        if self.connHandler.is_connection_receiver_connected():
            self.connHandler.send_exit_client_req(
                self.clientContext['username'], self.clientContext['roomCode'])
            self.connHandler.send_socket_disconnect_req()
            self.connHandler.kill_receiver()

    def display_system_message(self, message):
        self.chat.setFontItalic(True)
        self.chat.append("{}".format(message))
        self.chat.setFontItalic(False)

    def display_user_message(self, contents):
        self.chatEntryLine.clear()
        self.chatEntryLine.setText('')
        self.chat.append("{}: {}".format(
            contents['author'], contents['message']))

    def display_message(self, contents):
        # TODO: Remove message operations from ConnectionHandler, have it pass a dict to the signal.
        if contents['author'] == "SERVER":
            self.display_system_message(contents['message'])
        else:
            self.display_user_message(contents)

    def mouseMoveEvent(self, event):
        if self.artist != self.player:
            return

        x = event.x() - self.canvasContainer.x()
        y = event.y() - self.canvasContainer.y()

        if self.previousX is None:
            self.previousX = x
            self.previousY = y

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        painter.begin(self.canvas)
        painter.drawLine(self.previousX, self.previousY, x, y)
        painter.end()
        self.update()

        self.previousX = x
        self.previousY = y

        self.stroke.append((x, y))

    def mouseReleaseEvent(self, event):
        if self.artist != self.player:
            return

        self.strokes.append(self.stroke.copy())
        self.previousX = None
        self.previousY = None

        self.stroke = []
        # TODO: send stroke data to server

    def handleStartSignal(self, contents):
        self.artist = contents["artist"]
        self.display_system_message("Game started!")

        self.gameState = GameState.WORD_SELECTION

    def handlePlayerJoinedSignal(self, contents):
        self.display_system_message(
            "{} joined the room.".format(contents["player"]))
        self.players[contents.player] = 0
        self.updateScoreboard()

    def handlePlayerLeftSignal(self, contents):
        self.display_system_message(
            "{} left the room.".format(contents["player"]))
        del self.players[contents.player]
        self.updateScoreboard()
        # TODO: Handle all them edge cases.
        # TODO: What if the artist leaves, what if the owner leaves, what if the owner is left alone.

    def handleArtistChangeSignal(self, contents):
        # TODO: This drawings.append should be somewhere else, like in "guessing_over_signal", since now it won't fire on game over
        self.drawings.append(self.strokes.copy())
        self.display_system_message(
            "{} is now the artist.".format(contents["artist"]))
        self.artist = contents["artist"]
        if self.player == self.artist:
            self.undoButton.setDisabled(False)
            self.clearButton.setDisabled(False)
        else:
            self.undoButton.setDisabled(True)
            self.clearButton.setDisabled(True)
        self.clear()
        self.gameState = GameState.WORD_SELECTION

    def handleSelectPromptSignal(self, contents):
        # TODO: Display a popup with 3 prompts given by the server to select from, message selection to server
        self.gameState = GameState.WORD_SELECTION
        # TODO: For now select the first available prompt from contents['prompts']
        # TODO: Send a message to server

    def handlePromptSelectedSignal(self, contents):
        if self.player == self.artist:
            self.hint = contents["prompt"]
        else:
            self.hint = len(contents["prompt"]) * "_"
        self.hints.setText(self.hint)
        self.gameState = GameState.DRAWING

    def handleStrokeSignal(self, stroke):
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
        self.display_system_message(
            "{} guessed right!".format(contents["player"]))
        self.players[contents["player"]] += contents["score_awarded"]
        self.players[self.artist] += contents["artist_score_awarded"]
        self.updateScoreboard()
        pass

    def handleGameOverSignal(self, contents):
        self.gameState = GameState.POSTGAME
        self.players = contents["final_scores"]
        self.artist = ""
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
            self.display_system_message("It's a tie!")
        else:
            self.display_system_message("{} has won!".format(winner))
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
                painter.drawLine(stroke[i][0], stroke[i]
                                 [1], stroke[i + 1][0], stroke[i + 1][1])
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
        self.chatEntryLine.clear()
        self.chatEntryLine.setText('')
        self.connHandler.send_chat_msg_req(
            self.clientContext['username'], self.clientContext['roomCode'], message)

    def disconnect_clicked(self):
        self.connHandler.send_exit_client_req(
            self.clientContext['username'], self.clientContext['roomCode'])
        self.switch_window.emit()

    def start_clicked(self):
        self.connHandler.send_start_game_req(
            self.clientContext['username'], self.clientContext['roomCode'])


if __name__ == '__main__':
    pass
