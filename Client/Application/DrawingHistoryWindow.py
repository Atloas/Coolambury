from PyQt5 import QtWidgets, QtGui


class DrawingHistoryWindow(QtWidgets.QWidget):
    def __init__(self, drawings):
        QtWidgets.QWidget.__init__(self)

        # Assumes drawings isn't empty
        # copy()?
        self.drawings = drawings
        self.index = 0

        # Window
        self.rootVBox = QtWidgets.QVBoxLayout()

        self.canvas = QtGui.QPixmap(400, 300)
        self.canvas.fill(QtGui.QColor("white"))
        self.canvasContainer = QtWidgets.QLabel()
        self.canvasContainer.setPixmap(self.canvas)
        self.rootVBox.addWidget(self.canvasContainer)

        self.controlsHBox = QtWidgets.QHBoxLayout()
        self.rootVBox.addLayout(self.controlsHBox)

        self.previousButton = QtWidgets.QPushButton("<")
        self.previousButton.clicked.connect(self.previousClicked)
        self.previousButton.setDisabled(True)
        self.controlsHBox.addWidget(self.previousButton)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(self.saveClicked)
        self.controlsHBox.addWidget(self.saveButton)

        self.nextButton = QtWidgets.QPushButton(">")
        self.nextButton.clicked.connect(self.nextClicked)
        if len(self.drawings) == 1:
            self.nextButton.setDisabled(True)
        self.controlsHBox.addWidget(self.nextButton)

        self.setLayout(self.rootVBox)
        #self.setFixedSize(self.size())

        self.draw()

        self.show()

    # TODO: in stead of a label as canvasContainer make a Canvas(QtWidgets.Label) class that handles all drawing?
    def draw(self):
        strokes = self.drawings[self.index]
        painter = QtGui.QPainter(self.canvasContainer.pixmap())
        self.configurePen(painter)
        painter.eraseRect(0, 0, self.canvas.width(), self.canvas.height())
        for stroke in strokes:
            for i in range(len(stroke) - 1):
                painter.drawLine(stroke[i][0], stroke[i][1], stroke[i + 1][0], stroke[i + 1][1])
        painter.end()
        self.update()

    def configurePen(self, painter):
        pen = painter.pen()
        pen.setWidth(4)
        pen.setColor(QtGui.QColor("black"))
        painter.setPen(pen)

    def previousClicked(self):
        self.index -= 1
        if self.index == 0:
            self.previousButton.setDisabled(True)
        self.nextButton.setDisabled(False)
        self.draw()

    def nextClicked(self):
        self.index += 1
        if self.index == len(self.drawings) - 1:
            self.nextButton.setDisabled(True)
        self.previousButton.setDisabled(False)
        self.draw()

    def saveClicked(self):
        # TODO: Test this (and everything else, but especially this)
        dialogResult = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Drawing', '.', 'PNG', 'PNG')
        filename = dialogResult[0] + ".png"
        self.canvasContainer.pixmap().save(filename, "png")
