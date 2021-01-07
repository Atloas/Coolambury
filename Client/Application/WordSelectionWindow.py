from PyQt5 import QtWidgets, QtCore
import logging


class WordSelectionWindow(QtWidgets.QWidget):
    prompt_locally_selected_signal = QtCore.pyqtSignal(dict)

    def __init__(self, words):
        super().__init__()
        self.words = words
        logging.debug(
            '[WordSelectionWindow] Window Initialization with words: {}'.format(self.words))
        self.rootHBox = QtWidgets.QHBoxLayout()
        self.setLayout(self.rootHBox)
        self.setWindowTitle("Choose your word")

        # This could be done better, like with a list of buttons. Similarly the event handlers for button clicks
        self.wordButton0 = QtWidgets.QPushButton(self.words[0])
        self.wordButton0.clicked.connect(self.wordButton0Clicked)
        self.rootHBox.addWidget(self.wordButton0)

        self.wordButton1 = QtWidgets.QPushButton(self.words[1])
        self.wordButton1.clicked.connect(self.wordButton1Clicked)
        self.rootHBox.addWidget(self.wordButton1)

        self.wordButton2 = QtWidgets.QPushButton(self.words[2])
        self.wordButton2.clicked.connect(self.wordButton2Clicked)
        self.rootHBox.addWidget(self.wordButton2)

        self.show()

        self.setFixedSize(self.size())

    def closeEvent(self, event):
        logging.debug('[WordSelectionWindow] Closing...')

    def wordButton0Clicked(self):
        self.prompt_locally_selected_signal.emit(
            {"selected_word": self.words[0]})
        self.close()

    def wordButton1Clicked(self):
        self.prompt_locally_selected_signal.emit(
            {"selected_word": self.words[1]})
        self.close()

    def wordButton2Clicked(self):
        self.prompt_locally_selected_signal.emit(
            {"selected_word": self.words[2]})
        self.close()
