from GameWindow import GameWindow
from StartWindow import StartWindow


class WindowController:

    def __init__(self):
        self.window = None

    def show_start(self):
        if self.window is not None:
            self.window.close()
        self.window = StartWindow()
        self.window.switch_window.connect(self.show_start)  # Should be show_game, this is for debugging
        self.window.show()

    def show_game(self, roomNumber):
        self.window.close()
        self.window = GameWindow(roomNumber)
        self.window.switch_window.connect(self.show_start)
        self.window.show()
