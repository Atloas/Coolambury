import random
import string

def generate_unique_code(length, rooms):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    while result_str in rooms:
        result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str

def build_chat_msg_bc(user_name, message):
    chat_msg = {
        'msg_name': 'NewChatMessage',
        'author': user_name,
        'message': message
    }

    return chat_msg

def build_ok_create_room_resp(room_code):
    resp = {
        'msg_name': 'CreateRoomResp',
        'status': 'OK',
        'room_code': room_code
    }

    return resp

def build_not_ok_create_room_resp():
    resp = {
        'status': 'NOT_OK'
    }

    return resp

def build_ok_join_room_resp():
    resp = {
        'msg_name': 'JoinRoomResp',
        'status': 'OK'
    }

    return resp

def build_not_ok_join_room_resp():
    resp = {
        'msg_name': 'JoinRoomResp',
        'status': 'NOT_OK'
    }

    return resp

def build_join_notification(joined_user):
    join_notification = build_chat_msg_bc(
                            'SERVER',
                            '{} has joined the game'.format(joined_user))
    
    return join_notification
    