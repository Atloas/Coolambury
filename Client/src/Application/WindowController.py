from .GameWindow import GameWindow
from .StartWindow import StartWindow


class WindowController:

    def __init__(self):
        self.startWindow = None
        self.gameWindow = None

    def show_start(self):
        self.startWindow = StartWindow()
        # TODO: Should be show_game, this is for debugging
        self.startWindow.switch_window.connect(self.show_game)
        if self.gameWindow is not None:
            self.gameWindow.close()
        self.startWindow.show()

    def show_game(self, roomNumber):
        self.gameWindow = GameWindow(roomNumber)
        self.gameWindow.switch_window.connect(self.show_start)
        self.startWindow.close()
        self.gameWindow.show()
