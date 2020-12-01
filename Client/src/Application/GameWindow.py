from PyQt5 import QtCore, QtWidgets, QtGui


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self, roomCode):
        QtWidgets.QWidget.__init__(self)
        self.roomCode = roomCode
        self.setWindowTitle("Coolambury: {}".format(self.roomCode))

        # TODO: Drawing
        self.vBox = QtWidgets.QVBoxLayout()

        self.topHBox = QtWidgets.QHBoxLayout()

        self.bottomHBox = QtWidgets.QHBoxLayout()

        self.disconnectButton = QtWidgets.QPushButton("Disconnect")
        self.disconnectButton.clicked.connect(self.disconnect_clicked)
        self.topHBox.addWidget(self.disconnectButton)

        self.hints = QtWidgets.QLabel("*HINTS*")   # TODO
        self.topHBox.addWidget(self.hints)

        self.scoreboard = QtWidgets.QTableView()
        self.bottomHBox.addWidget(self.scoreboard)

        self.canvasContainer = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)
        self.canvasContainer.setPixmap(canvas)
        self.bottomHBox.addWidget(self.canvasContainer)

        self.chat = QtWidgets.QLabel("*CHAT*")
        self.bottomHBox.addWidget(self.chat)

        self.vBox.addLayout(self.topHBox)
        self.vBox.addLayout(self.bottomHBox)

        self.setLayout(self.vBox)


    def disconnect_clicked(self):
        # TODO: disconnect socket
        self.switch_window.emit()
