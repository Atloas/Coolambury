from .GameWindow import GameWindow
from .StartWindow import StartWindow
from Communication.ConnectionHandler import ConnectionHandler
import logging
from Utils.PopUpWindow import PopUpWindow


class WindowController:

    def __init__(self, connHandler):
        self.connHandler = connHandler
       
        self.clientContext = {}
        self.clientContext['username'] = ''
        self.clientContext['roomCode'] = ''
        self.startWindow = StartWindow(self.connHandler, self.clientContext)
        self.gameWindow = GameWindow(self.clientContext, self.connHandler)
        self.gameWindow.close()

    def show_start(self):
        # TODO: Should be show_game, this is for debugging
        self.connHandler.switch_window.connect(self.show_game)
        if self.gameWindow is not None:
            self.gameWindow.close()
        self.startWindow.show()

    def show_game(self, roomCode):
        self.gameWindow.switch_window.connect(self.show_start)
        self.clientContext['roomCode'] = roomCode
        self.startWindow.close()
        self.gameWindow.show()



if __name__ == '__main__':
    pass
