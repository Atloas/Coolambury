from PyQt5 import QtWidgets, QtCore


class WordSelectionWindow(QtWidgets.QWidget):
    prompt_locally_selected_signal = QtCore.pyqtSignal(dict)

    def __init__(self, words):
        QtWidgets.QWidget.__init__(self)

        self.words = words

        self.rootHBox = QtWidgets.QHBoxLayout()

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

        self.setLayout(self.rootHBox)

        self.show()

    def wordButton0Clicked(self):
        self.prompt_locally_selected_signal.emit({'word': self.words[0]})
        self.close()

    def wordButton1Clicked(self):
        self.prompt_locally_selected_signal.emit({'word': self.words[1]})
        self.close()

    def wordButton2Clicked(self):
        self.prompt_locally_selected_signal.emit({'word': self.words[2]})
        self.close()
