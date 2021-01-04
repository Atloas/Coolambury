import logging
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
    switch_window = QtCore.pyqtSignal()
    key_pressed_signal = QtCore.pyqtSignal(QtCore.QEvent)
    word_locally_selected_signal = QtCore.pyqtSignal(dict)

    def __init__(self, clientContext, connHandler):
        # TODO: Reset window's state on switch
        QtWidgets.QWidget.__init__(self)

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
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.setMaximumSize(100, 50)
        self.startButton.clicked.connect(self.start_clicked)
        self.topHBox.addWidget(self.disconnectButton)
        self.topHBox.addWidget(self.startButton)

        self.hints = QtWidgets.QLabel("*HINTS*")
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

        self.connectSignals()

    def connectSignals(self):
        self.connHandler.chat_message_signal.connect(self.display_user_message)
        self.connHandler.start_game_signal.connect(self.handleStartGameSignal)
        self.connHandler.word_selection_signal.connect(
            self.handleWordSelectionSignal)
        self.connHandler.player_joined_signal.connect(
            self.handlePlayerJoinedSignal)
        self.connHandler.player_left_signal.connect(
            self.handlePlayerLeftSignal)
        self.connHandler.word_selected_signal.connect(
            self.handleWordSelectedSignal)
        self.connHandler.draw_stroke_signal.connect(self.handleStrokeSignal)
        self.connHandler.undo_last_stroke_signal.connect(self.handleUndoSignal)
        self.connHandler.clear_canvas_signal.connect(self.handleClearCanvasSignal)
        self.connHandler.guess_correct_signal.connect(
            self.handleGuessCorrectSignal)
        self.connHandler.artist_change_signal.connect(
            self.handleArtistChangeSignal)
        self.connHandler.game_over_signal.connect(self.handleGameOverSignal)
        self.connHandler.room_list_signal.connect(self.handleGameRoomListResp)

    def initialize_room(self, contents):
        # Set room state to a fresh one with just the owner
        self.gameState = GameState.PREGAME
        self.owner = contents['owner']
        self.players = contents['players']
        if not self.players:
            self.players[self.clientContext["username"]] = 0
        self.hint = "PREGAME"
        self.previousX = None
        self.previousY = None
        self.drawings = []
        self.strokes = []
        self.stroke = []

        self.clearCanvas()
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
        self.chat.setFontWeight(2)
        self.chat.append("{}".format(message))
        self.chat.setFontItalic(False)
        self.chat.setFontWeight(1)

    def display_user_message(self, contents):
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

    def handleStartGameSignal(self, contents):
        logging.debug("Handling start_game_signal")
        self.display_system_message("Game started!")

    def handlePlayerJoinedSignal(self, contents):
        logging.debug("Handling player_joined_signal")
        self.display_system_message(
            "{} joined the room.".format(contents["player"]))
        self.players[contents["player"]] = 0
        self.updateScoreboard()

    def handlePlayerLeftSignal(self, contents):
        logging.debug("Handling player_left_signal")
        self.display_system_message(
            "{} left the room.".format(contents["player"]))
        del self.players[contents["player"]]
        self.updateScoreboard()
        # TODO: Handle all them edge cases.
        # TODO: What if the artist leaves, what if the owner leaves, what if the owner is left alone.

    def handleArtistChangeSignal(self, contents):
        logging.debug("Handling artist_changed_signal")
        # TODO: This drawings.append should be somewhere else, like in "guessing_over_signal", since now it won't fire on game over
        self.drawings.append(self.strokes.copy())
        self.display_system_message(
            "{} is now the artist.".format(contents["artist"]))
        self.artist = contents["artist"]
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

    def handleWordSelectionSignal(self, contents):
        logging.debug("Handling word_selection_signal")
        self.wordSelectionWindow = WordSelectionWindow(contents["word_list"])
        self.wordSelectionWindow.prompt_locally_selected_signal.connect(
            self.handleWordLocallySelectedSignal)
        self.gameState = GameState.WORD_SELECTION

    def handleWordLocallySelectedSignal(self, contents):
        logging.debug("Handling word_locally_selected_signal")
        logging.debug("[Word Selection] Selected word = {}".format(
            contents['selected_word']))
        self.hints.setText(contents["selected_word"])

        self.connHandler.send_word_selection_resp(
            self.clientContext['username'], self.clientContext['roomCode'], contents['selected_word'])

    def handleWordSelectedSignal(self, contents):
        logging.debug("Handling word_selected_signal")
        if self.player == self.artist:
            return
        else:
            self.hints.setText(contents["word_hint"])
        self.gameState = GameState.DRAWING

    def handleStrokeSignal(self, contents):
        logging.debug("Handling draw_stroke_signal")
        stroke = contents["stroke_coordinates"]
        self.strokes.append(stroke.copy())

        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        painter.begin(self.canvas)
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
        logging.debug("Handling undo_last_stroke_signal")
        self.undo()

    def handleClearCanvasSignal(self):
        logging.debug("Handling clear_canvas_signal")
        self.stroke = []
        self.strokes = []
        self.clearCanvas()

    def handleGuessCorrectSignal(self, contents):
        self.display_system_message(
            "{} guessed the word: {}!".format(contents["user_name"], contents["word"]))

        self.players = contents['score_awarded']
        self.updateScoreboard()

    def handleGameOverSignal(self, contents):
        logging.debug("Handling game_over_signal")
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
            self.drawingHistoryWindow = DrawingHistoryWindow(self.drawings)
        self.drawings = []

    def handleGameRoomListResp(self, contents):
        # TODO: Implement for room listing
        pass

    def undoClicked(self):
        self.undo()
        self.connHandler.send_undo_last_stroke_req(
            self.clientContext['username'], self.clientContext['roomCode'])

    def clearCanvasClicked(self):
        self.stroke = []
        self.strokes = []
        self.clear()
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

    def updateScoreboard(self):
        self.scoreboard.setRowCount(len(self.players))
        playerNumber = 0
        for player in self.players:
            score = self.players[player]
            nameItem = QtWidgets.QTableWidgetItem(player)
            scoreItem = QtWidgets.QTableWidgetItem(str(score))
            self.scoreboard.setItem(playerNumber, 0, nameItem)
            self.scoreboard.setItem(playerNumber, 1, scoreItem)
            playerNumber += 1

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
