from PyQt5 import QtCore, QtWidgets, QtGui


class GameWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self, roomNumber):
        QtWidgets.QWidget.__init__(self)
        self.roomNumber = roomNumber
        self.setWindowTitle("Coolambury: {}".format(self.roomNumber))

        # TODO: Drawing
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
