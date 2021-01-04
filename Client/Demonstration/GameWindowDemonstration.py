from PyQt5 import QtCore, QtWidgets, QtGui

from ..Application.GameWindow import GameWindow


class SignalWindow(QtWidgets.QWidget):
    player_joined_signal = QtCore.pyqtSignal(dict)
    player_left_signal = QtCore.pyqtSignal(dict)
    word_hint_signal = QtCore.pyqtSignal(dict)
    draw_stroke_signal = QtCore.pyqtSignal(dict)
    undo_last_stroke_signal = QtCore.pyqtSignal()
    clear_canvas_signal = QtCore.pyqtSignal()
    guess_correct_signal = QtCore.pyqtSignal(dict)
    chat_message_signal = QtCore.pyqtSignal(str)
    artist_change_signal = QtCore.pyqtSignal(dict)
    game_over_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.rootVBox = QtWidgets.QVBoxLayout()

        self.playerJoinedButton = QtWidgets.QPushButton("Player Joined")
        self.playerJoinedButton.clicked.connect(self.playerJoinedClicked)
        self.rootVBox.addWidget(self.playerJoinedButton)

        self.playerLeftButton = QtWidgets.QPushButton("Player Left")
        self.playerLeftButton.clicked.connect(self.playerLeftClicked)
        self.rootVBox.addWidget(self.playerLeftButton)

        self.wordSelectedButton = QtWidgets.QPushButton("Word Selected")
        self.wordSelectedButton.clicked.connect(self.wordSelectedClicked)
        self.rootVBox.addWidget(self.wordSelectedButton)

        self.strokeButton = QtWidgets.QPushButton("Stroke")
        self.strokeButton.clicked.connect(self.strokeClicked)
        self.rootVBox.addWidget(self.strokeButton)

        self.undoButton = QtWidgets.QPushButton("Undo")
        self.undoButton.clicked.connect(self.undoClicked)
        self.rootVBox.addWidget(self.undoButton)

        self.clearButton = QtWidgets.QPushButton("Clear")
        self.clearButton.clicked.connect(self.clearClicked)
        self.rootVBox.addWidget(self.clearButton)

        self.guessCorrectButton = QtWidgets.QPushButton("Guess Correct")
        self.guessCorrectButton.clicked.connect(self.guessCorrectClicked)
        self.rootVBox.addWidget(self.guessCorrectButton)

        self.chatMessageButton = QtWidgets.QPushButton("Chat Message")
        self.chatMessageButton.clicked.connect(self.chatMessageClicked)
        self.rootVBox.addWidget(self.chatMessageButton)

        self.artistChangeButton = QtWidgets.QPushButton("Artist Change")
        self.artistChangeButton.clicked.connect(self.artistChangeClicked)
        self.rootVBox.addWidget(self.artistChangeButton)

        self.gameOverButton = QtWidgets.QPushButton("Game Over")
        self.gameOverButton.clicked.connect(self.gameOverClicked)
        self.rootVBox.addWidget(self.gameOverButton)

        self.setLayout(self.rootVBox)

    def playerJoinedClicked(self):
        self.player_joined_signal.emit({"player": "User2"})

    def playerLeftClicked(self):
        self.player_left_signal.emit({"player": "User2"})

    def wordSelectionClicked(self):
        self.word_hint_signal.emit({"words": ["Apple", "Boat", "Dog"]})

    def strokeClicked(self):
        self.draw_stroke_signal.emit({"stroke": [(10, 10), (100, 100)]})

    def undoClicked(self):
        self.undo_last_stroke_signal.emit()

    def clearClicked(self):
        self.clear_canvas_signal.emit()

    def guessCorrectClicked(self):
        self.guess_correct_signal.emit(
            {"player": "User2", "scoreAwarded": 100})

    def chatMessageClicked(self):
        self.chat_message_signal.emit({"author": "User2", "message": "Hello!"})

    def artistChangeClicked(self):
        self.artist_change_signal.emit({"artist": "User2"})

    def gameOverClicked(self):
        self.game_over_signal.emit(
            {"final_scores": {"User1": 0, "User2": 10000}})


if __name__ == "__main__":
    GameWindow({"username": "User1", "roomCode": "test"}, None)
    SignalWindow()
