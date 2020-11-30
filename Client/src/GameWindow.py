from PyQt5 import QtCore, QtWidgets, QtGui


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self, roomCode):
        QtWidgets.QWidget.__init__(self)
        self.roomCode = roomCode
        self.setWindowTitle("Coolambury: {}".format(self.roomCode))

        # TODO: Drawing
        self.vBox = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)
        self.label.setPixmap(canvas)

        self.vBox.addWidget(self.label)
