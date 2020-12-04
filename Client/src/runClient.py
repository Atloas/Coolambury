from PyQt5.QtWidgets import QApplication
from Application.WindowController import WindowController
import sys
import logging

# for windows:
# $env:PYTHONPATH = "."
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication([])
    windowController = WindowController()
    windowController.show_start()
    sys.exit(app.exec_())
