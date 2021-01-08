import logging
import operator
import threading
from enum import Enum
from PyQt5 import QtCore, QtWidgets, QtGui
from .WordSelectionWindow import WordSelectionWindow
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


class GameWindow(QtWidgets.QWidget):
    thread_lock = threading.Lock()
    switch_window = QtCore.pyqtSignal()
    key_pressed_signal = QtCore.pyqtSignal(QtCore.QEvent)
    word_locally_selected_signal = QtCore.pyqtSignal(dict)

    def __init__(self, clientContext, connHandler):
        # TODO: Reset window's state on switch
        QtWidgets.QWidget.__init__(self)
        with self.thread_lock:
            logging.debug("[GAMEWINDOW] Creating Game Window instance...")
            self.clientContext = clientContext
            self.connHandler = connHandler
            self.setWindowTitle("Coolambury [{}] {}".format(
                self.clientContext['username'],
                self.clientContext['roomCode']))

            # Game
            # Contains a dict of all player names and their scores, ex. {"Atloas": 100, "loska": 110}
            # Player drawing order enforced by server?
            self.gameState = None
            self.player = self.clientContext['username']
            self.owner = None
            self.players = {}
            self.players[self.player] = 0
            self.artist = None
            # The hint text, modifiable on server request.
            # For the painter, should display the full word. Placeholder for now.
            self.hint = "____"

            self.wordSelectionWindow = None
            self.drawingHistoryWindow = None

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
            self.topHBox.addWidget(self.disconnectButton)

            self.startButton = QtWidgets.QPushButton("Start")
            self.startButton.setMaximumSize(100, 50)
            self.startButton.clicked.connect(self.start_clicked)
            self.topHBox.addWidget(self.startButton)

            self.hints = QtWidgets.QLabel("")
            self.topHBox.addWidget(self.hints)

            self.scoreboardColumnLabels = ['Nickname', 'Score']
            self.scoreboard = QtWidgets.QTableWidget()
            self.scoreboard.verticalHeader().hide()
            self.scoreboard.setColumnCount(len(self.scoreboardColumnLabels))
            self.scoreboard.setHorizontalHeaderLabels(
                self.scoreboardColumnLabels)
            for column in range(len(self.scoreboardColumnLabels)):
                self.scoreboard.setColumnWidth(column, 125)

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

            self.clearCanvasButton = QtWidgets.QPushButton("Clear")
            self.clearCanvasButton.setDisabled(True)
            self.clearCanvasButton.clicked.connect(self.clearCanvasClicked)
            self.controlsHBox.addWidget(self.clearCanvasButton)

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
            # self.setFixedSize(self.size())
            self.updateScoreboard()

            self.connectSignals()
            logging.debug("[GAMEWINDOW] Game Window created...")

    def connectSignals(self):
        self.connHandler.chat_message_signal.connect(self.display_message)
        self.connHandler.start_game_signal.connect(self.handleStartGameSignal)
        self.connHandler.word_selection_signal.connect(
            self.handleWordSelectionSignal)
        self.connHandler.player_joined_signal.connect(
            self.handlePlayerJoinedSignal)
        self.connHandler.player_left_signal.connect(
            self.handlePlayerLeftSignal)
        self.connHandler.word_hint_signal.connect(
            self.handleWordHintSignal)
        self.connHandler.draw_stroke_signal.connect(self.handleStrokeSignal)
        self.connHandler.undo_last_stroke_signal.connect(self.handleUndoSignal)
        self.connHandler.clear_canvas_signal.connect(
            self.handleClearCanvasSignal)
        self.connHandler.guess_correct_signal.connect(
            self.handleGuessCorrectSignal)
        self.connHandler.artist_change_signal.connect(
            self.handleArtistChangeSignal)
        self.connHandler.game_over_signal.connect(self.handleGameOverSignal)
        self.connHandler.scoreboard_update_signal.connect(
            self.updateScoreboardData)

    def closeEvent(self, event):
        logging.debug(
            "[EXITING ATTEMPT] Client is requesting for client exit")
        if self.connHandler.is_connection_receiver_connected():
            self.connHandler.send_exit_client_req(
                self.clientContext['username'], self.clientContext['roomCode'])
            self.connHandler.send_socket_disconnect_req()
            self.connHandler.kill_receiver()

    def display_system_message(self, message):
        self.chat.append("<b>{}</b>".format(message))

    def display_user_message(self, message):
        self.chat.append("{}: {}".format(
            message['author'], message['message']))

    def display_message(self, message):
        if message['author'] == "SERVER":
            self.display_system_message(message['message'])
        else:
            self.display_user_message(message)

    # DO NOT RENAME, breaks drawing
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

        self.connHandler.send_draw_stroke_req(self.clientContext['username'],
                                              self.clientContext['roomCode'],
                                              self.stroke.copy())
        self.stroke = []

    def handleStartGameSignal(self, message):
        self.startButton.setDisabled(True)
        logging.debug("[GameWindow] Handling start_game_signal")
        self.display_system_message("Game started!")
        self.players = message['score_awarded']
        self.updateScoreboard()

    def handlePlayerJoinedSignal(self, message):
        logging.debug("[GameWindow] Handling player_joined_signal")
        self.display_system_message(
            "{} joined the room.".format(message["player"]))
        self.players[message["player"]] = 0
        self.updateScoreboard()
        self.update()

    def handlePlayerLeftSignal(self, message):
        logging.debug("[GameWindow] Handling player_left_signal")
        self.display_system_message(
            "{} left the room.".format(message["player"]))
        del self.players[message["player"]]
        self.updateScoreboard()
        # TODO: Handle all them edge cases.
        # TODO: What if the artist leaves, what if the owner leaves, what if the owner is left alone.

    def handleArtistChangeSignal(self, message):
        logging.debug("[GameWindow] Handling artist_changed_signal")
        if self.wordSelectionWindow is not None:
            self.wordSelectionWindow.close()
        self.display_system_message(
            "{} is now the artist.".format(message["artist"]))
        self.artist = message["artist"]
        if self.player == self.artist:
            self.undoButton.setDisabled(False)
            self.clearCanvasButton.setDisabled(False)
        else:
            self.undoButton.setDisabled(True)
            self.clearCanvasButton.setDisabled(True)
        self.stroke = []
        self.strokes = []
        self.clearCanvas()
        self.gameState = GameState.WORD_SELECTION

    def handleWordSelectionSignal(self, message):
        logging.debug("[GameWindow] Handling word_selection_signal")
        self.wordSelectionWindow = WordSelectionWindow(message["word_list"])
        self.wordSelectionWindow.prompt_locally_selected_signal.connect(
            self.handleWordLocallySelectedSignal)
        self.gameState = GameState.WORD_SELECTION

    def handleWordLocallySelectedSignal(self, message):
        logging.debug("[GameWindow] Handling word_locally_selected_signal")
        logging.debug("[GameWindow] [Word Selection] Selected word = {}".format(
            message['selected_word']))
        self.hints.setText(message["selected_word"])

        self.connHandler.send_word_selection_resp(
            self.clientContext['username'], self.clientContext['roomCode'], message['selected_word'])

    def handleWordHintSignal(self, message):
        logging.debug("[GameWindow] Handling word_hint_signal")
        if self.player == self.artist:
            return
        else:
            self.hint = ""
            for i in range(len(message["word_hint"]) - 1):
                self.hint += message["word_hint"][i] + " "
            self.hint += "_"
            self.hints.setText(self.hint)
        self.gameState = GameState.DRAWING

    def handleStrokeSignal(self, message):
        logging.debug("[GameWindow] Handling draw_stroke_signal")
        stroke = message["stroke_coordinates"]
        self.strokes.append(stroke.copy())

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        if len(stroke) == 1:
            painter.drawLine(stroke[0][0], stroke[0][1],
                             stroke[0][0], stroke[0][1])
        else:
            for i in range(len(stroke) - 1):
                painter.drawLine(stroke[i][0], stroke[i][1],
                                 stroke[i + 1][0], stroke[i + 1][1])
        painter.end()
        self.update()

    def handleUndoSignal(self):
        logging.debug("[GameWindow] Handling undo_last_stroke_signal")
        self.undo()

    def handleClearCanvasSignal(self):
        logging.debug("[GameWindow] Handling clear_canvas_signal")
        self.stroke = []
        self.strokes = []
        self.clearCanvas()

    def handleGuessCorrectSignal(self, message):
        logging.debug("[GameWindow] Handling guess_correct_signal")
        self.display_system_message(
            "{} guessed the word: {}!".format(message["user_name"], message["word"]))
        self.drawings.append(self.strokes.copy())
        self.players = message['score_awarded']
        self.updateScoreboard()

    def handleGameOverSignal(self, message):
        self.startButton.setDisabled(False)
        logging.debug("[GameWindow] Handling game_over_signal")
        self.gameState = GameState.POSTGAME
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
            self.drawingHistoryWindow = DrawingHistoryWindow(self.drawings)
        self.drawings = []

    def undoClicked(self):
        self.undo()
        self.connHandler.send_undo_last_stroke_req(
            self.clientContext['username'], self.clientContext['roomCode'])

    def clearCanvasClicked(self):
        self.stroke = []
        self.strokes = []
        self.clearCanvas()
        self.connHandler.send_clear_canvas_req(
            self.clientContext['username'], self.clientContext['roomCode'])

    def redraw(self):
        self.clearCanvas()
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        for stroke in self.strokes:
            if len(stroke) == 1:
                painter.drawLine(stroke[0][0], stroke[0][1],
                                 stroke[0][0], stroke[0][1])
            else:
                for i in range(len(stroke) - 1):
                    painter.drawLine(stroke[i][0], stroke[i][1],
                                     stroke[i + 1][0], stroke[i + 1][1])
        painter.end()
        self.update()

    def undo(self):
        self.stroke = []
        if len(self.strokes) > 0:
            self.strokes.pop()
        self.redraw()

    def clearCanvas(self):
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        painter.eraseRect(0, 0, self.canvas.width(), self.canvas.height())
        painter.end()
        self.update()

    def configurePen(self, painter):
        pen = painter.pen()
        pen.setWidth(4)
        pen.setColor(QtGui.QColor("black"))
        painter.setPen(pen)

    def updateScoreboardData(self, message):
        self.players = message['users_in_room']
        self.updateScoreboard()

    def updateScoreboard(self):
        # TODO: consider renaming players to scoreboardData
        self.scoreboard.setRowCount(len(self.players))
        playerNumber = 0
        sortedPlayers = sorted(self.players.items(),
                               reverse=True, key=operator.itemgetter(1))
        for player in sortedPlayers:
            playerName = player[0]
            score = player[1]
            nameItem = QtWidgets.QTableWidgetItem(playerName)
            scoreItem = QtWidgets.QTableWidgetItem(str(score))
            self.scoreboard.setItem(playerNumber, 0, nameItem)
            self.scoreboard.setItem(playerNumber, 1, scoreItem)
            playerNumber += 1

    def newChatMessage(self):
        message = self.chatEntryLine.text()
        # TODO: Why clear() and setText('')? Shouldn't one suffice?
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
