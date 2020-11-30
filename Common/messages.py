class MessageHeader:
    def __init__(self, length, name):
        self.length = length
        self.name = name

class CreateRoom:
    def __init__(self):
        self.username = ''
        self.roomname = ''
