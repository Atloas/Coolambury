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
        'msg_name': 'ChatMessageBc',
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


def build_ok_join_room_resp(users):
    resp = {
        'msg_name': 'JoinRoomResp',
        'status': 'OK',
        'users': users
    }

    return resp


def build_not_ok_join_room_resp(info=None):
    resp = {
        'msg_name': 'JoinRoomResp',
        'status': 'NOT_OK',
    }
    
    if info is not None:
        resp['info'] = info

    if info is not None:
        resp['info'] = info

    return resp


def build_join_notification(joined_user):
    join_notification = build_chat_msg_bc(
                            'SERVER',
                            '{} has joined the game'.format(joined_user))
    return join_notification
    
def build_leave_notification(user_name):
    join_notification = build_chat_msg_bc(
                            'SERVER',
                            '{} has left the game'.format(user_name))
    
    return join_notification
    
def build_start_game_resp_ok(info=None):
    resp = {
        'msg_name': 'StartGameResp',
        'status': 'OK',
    }
    if info is not None:
        resp['info'] = info

    return resp

def build_start_game_resp_not_ok(info=None):
    resp = {
        'msg_name': 'StartGameResp',
        'status': 'NOT_OK',
    }
    
    if info is not None:
        resp['info'] = info

    return resp

def build_word_selection_req(user_name, room_code, word_list):
    req = {
        'msg_name': 'WordSelectionReq',
        'user_name': user_name,
        'room_code': room_code,
        'word_list': word_list
    }

    return req