from PyQt5.QtWidgets import QApplication
from WindowController import WindowController
import sys


if __name__ == "__main__":
    app = QApplication([])
    windowController = WindowController()
    windowController.show_start()
    sys.exit(app.exec_())
