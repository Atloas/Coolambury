import msg_handling
import logging
import messages
from room import Room
import random
import string
import traceback


def generate_unique_code(length, rooms):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    while result_str in rooms:
        result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


class RoomNotExistsException(Exception):
    pass

class UsernameTakenException(Exception):
    pass


class JoinRoomReqHandler:
    def __init__(self, rooms, clients, server_config):
        self._rooms = rooms
        self._clients = clients
        self._server_config = server_config

    def handle(self, sender_conn, msg):
        try:
            if msg.room_code not in self._rooms:
                raise RoomNotExistsException()
            
            room = self._rooms[msg.room_code]

            if msg.user_name in room.joined_clients:
                raise UsernameTakenException()

            room.add_client(msg.user_name, sender_conn)

            resp = messages.JoinRoomResp()
            resp.status = 'OK'
            resp.return_message = 'Joined correctly'

            msg_handling.send(sender_conn, resp, self._server_config)

            logging.debug('[JOIN_ROOM_REQ_HANDLER] User {} joined to room {}'.format(
                msg.user_name, msg.room_code))

        except:
            traceback.print_exc()
            logging.error(
                '[JOIN_ROOM_REQ_HANDLER] Error ocured when handling message')
            resp = messages.JoinRoomResp()
            resp.status = 'NOT_OK'
            msg_handling.send(sender_conn, resp, self._server_config)
