from PyQt5 import QtWidgets, QtCore


class StartWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Coolambury")

        self.vBox = QtWidgets.QVBoxLayout()
        self.label1 = QtWidgets.QLabel('Enter your nickname:')
        self.lineEdit1 = QtWidgets.QLineEdit()
        self.lineEdit1.maxLength = 15
        self.label2 = QtWidgets.QLabel('Enter room code:')
        self.lineEdit2 = QtWidgets.QLineEdit()
        self.lineEdit2.maxLength = 4
        self.button = QtWidgets.QPushButton("Join room")
        self.button.clicked.connect(self.join_clicked)

        self.setLayout(self.vBox)
        self.vBox.addWidget(self.label1)
        self.vBox.addWidget(self.lineEdit1)
        self.vBox.addWidget(self.label2)
        self.vBox.addWidget(self.lineEdit2)
        self.vBox.addWidget(self.button)

    def validate_inputs(self):
        if True:  # self.lineEdit1.text and len(self.lineEdit2.text) == 4:
            return True
        else:
            return False

    def connect_to_room(self):
        # TODO
        return True

    def display_message(self, message):
        alert = QtWidgets.QMessageBox()
        alert.setText(message)
        alert.exec_()

    def join_clicked(self):
        if self.validate_inputs():
            if self.connect_to_room():
                self.switch_window.emit(self.lineEdit2.text)
            else:
                self.display_message("Could not connect to room!")
        else:
            self.display_message("invalid inputs!")
