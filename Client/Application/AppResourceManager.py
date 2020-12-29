from .GameWindow import GameWindow
from .StartWindow import StartWindow
from Communication.ConnectionHandler import ConnectionHandler
import logging
from Utils.PopUpWindow import PopUpWindow

# ApplicationResourcesManager
class AppResourceManager:

    def __init__(self, connHandler):
        self.connHandler = connHandler
        self.clientContext = {}
        self.clientContext['username'] = ''
        self.clientContext['roomCode'] = ''
        self.startWindow = StartWindow(self.connHandler, self.clientContext)
        self.gameWindow = None
        # TODO: sort out the parameter order:
        self.connHandler.switch_window.connect(self.show_game)
        self.startWindow.show()

    def show_start(self):
        if self.startWindow is not None:
            if self.gameWindow is not None and self.gameWindow.isVisible():
                self.gameWindow.hide()
            self.startWindow.setVisible(True)

    def show_game(self, roomCode):
        if roomCode != 'Joining':
            self.clientContext['roomCode'] = roomCode
        self.gameWindow = GameWindow(self.clientContext, self.connHandler)
        # TODO: Move to GameWindow.__init__()?
        self.gameWindow.switch_window.connect(self.show_start)
        self.startWindow.hide()
        self.gameWindow.show()


if __name__ == '__main__':
    pass
