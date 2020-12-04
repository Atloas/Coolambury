from PyQt5.QtWidgets import QApplication
from Application.WindowController import WindowController
import sys
import logging

from Communication.ConnectionHandler import ConnectionHandler
from Utils.PopUpWindow import PopUpWindow
import traceback

# for windows (PowerShell):
# $env:PYTHONPATH = "."
if __name__ == "__main__":
    try:
        connHandler = ConnectionHandler()
    except:
        traceback.print_exc()
        logging.debug("[SOCKET CONNECTION] Connection to server failed")
        PopUpWindow('Game server is unreachable!')
        exit()

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication([])
    windowController = WindowController(connHandler)
    windowController.show_start()
    sys.exit(app.exec_())
    connHandler.kill_receiver()
