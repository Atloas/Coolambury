from PyQt5.QtWidgets import QApplication
from Application.AppResourceManager import AppResourceManager
import sys
import logging

from Communication.ConnectionHandler import ConnectionHandler
from Utils.PopUpWindow import PopUpWindow

# for windows (PowerShell):
# $env:PYTHONPATH = "."
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('[STARTING] Client is being loaded ...')
    app = QApplication([])
    try:
        connHandler = ConnectionHandler()
    except:
        logging.debug("[SOCKET CONNECTION] Connection to server failed")
        PopUpWindow('Game server is unreachable!')
        exit()

    AppResourceManager = AppResourceManager(connHandler)
    logging.debug('[CLIENT STARTED]')
    AppResourceManager.show_start()
    sys.exit(app.exec_())
    connHandler.kill_receiver()
