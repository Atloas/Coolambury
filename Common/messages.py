class MessageHeader:
    def __init__(self, length, name):
        self.length = length
        self.name = name


class CreateRoomReq:
    def __init__(self):
        self.user_name = ''
        self.room_name = ''

    def __str__(self):
        return self.user_name + ' ' + self.room_name


class CreateRoomResp:
    def __init__(self):
        self.status = ''
        self.room_code = ''

    def __str__(self):
        return self.status + ' ' + self.room_code


class JoinRoomReq:
    def __init__(self):
        self.user_name = ''
        self.room_code = ''

    def __str__(self):
        return self.user_name + ' ' + self.room_code

class JoinRoomResp:
    def __init__(self):
        self.status = ''
        self.return_message = ''

    def __str__(self):
        return self.status + ' ' + self.return_message


class WriteChatReq:
    def __init__(self):
        self.user_name = ''
        self.room_code = ''
        self.message = ''


class NewChatMessage: # TODO: rename eg. ClientMsgBroadcast
    def __init__(self):
        self.author = ''
        self.message = ''

    def __str__(self):
        return self.author + ' ' + self.message


class ExitClientReq():
    def __init__(self):
        self.user_name = ''


class ExitClientResp():
    def __init__(self):
        self.status = ''
