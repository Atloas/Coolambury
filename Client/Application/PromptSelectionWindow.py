from PyQt5 import QtWidgets, QtCore


class PromptSelectionWindow(QtWidgets.QWidget):
    prompt_locally_selected_signal = QtCore.pyqtSignal(dict)

    def __init__(self, prompts):
        QtWidgets.QWidget.__init__(self)

        self.prompts = prompts

        self.rootHBox = QtWidgets.QHBoxLayout()

        # This could be done better, like with a list of buttons. Similarly the event handlers for button clicks
        self.promptButton0 = QtWidgets.QPushButton(self.prompts[0])
        self.promptButton0.clicked.connect(self.promptButton0Clicked)
        self.rootHBox.addWidget(self.promptButton0)

        self.promptButton1 = QtWidgets.QPushButton(self.prompts[1])
        self.promptButton1.clicked.connect(self.promptButton1Clicked)
        self.rootHBox.addWidget(self.promptButton1)

        self.promptButton2 = QtWidgets.QPushButton(self.prompts[2])
        self.promptButton2.clicked.connect(self.promptButton2Clicked)
        self.rootHBox.addWidget(self.promptButton2)

        self.show()

    def promptButton0Clicked(self):
        self.prompt_locally_selected_signal.emit({"prompt": self.prompts[0]})
        self.close()

    def promptButton1Clicked(self):
        self.prompt_locally_selected_signal.emit({"prompt": self.prompts[1]})
        self.close()

    def promptButton2Clicked(self):
        self.prompt_locally_selected_signal.emit({"prompt": self.prompts[2]})
        self.close()
