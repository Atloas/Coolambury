from PyQt5 import QtWidgets, QtCore


class StartWindow(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Coolambury")

        self.vBox = QtWidgets.QVBoxLayout()
        self.nicknameLabel = QtWidgets.QLabel('Enter your nickname:')
        self.nicknameField = QtWidgets.QLineEdit()
        self.nicknameField.maxLength = 15
        self.roomCodeLabel = QtWidgets.QLabel('Enter room code:')
        self.roomCodeField = QtWidgets.QLineEdit()
        self.roomCodeField.maxLength = 4
        self.joinButton = QtWidgets.QPushButton("Join room")
        self.joinButton.clicked.connect(self.join_clicked)

        self.setLayout(self.vBox)
        self.vBox.addWidget(self.nicknameLabel)
        self.vBox.addWidget(self.nicknameField)
        self.vBox.addWidget(self.roomCodeLabel)
        self.vBox.addWidget(self.roomCodeField)
        self.vBox.addWidget(self.joinButton)

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
                roomNumber = self.roomCodeField.text()
                self.switch_window.emit(roomNumber)
            else:
                self.display_message("Could not connect to room!")
        else:
            self.display_message("invalid inputs!")
