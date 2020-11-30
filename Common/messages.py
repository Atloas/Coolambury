class MessageHeader:
    def __init__(self, length, name):
        self.length = length
        self.name = name

class CreateRoomReq:
    def __init__(self):
        self.username = ''
        self.roomname = ''

    def __str__(self):
        return self.username + ' ' + self.roomname

class CreateRoomResp:
    def __init__(self):
        self.status = ''
        self.room_code = ''

    def __str__(self):
        return self.status + ' ' + self.room_code
