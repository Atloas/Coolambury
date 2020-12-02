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


class CreateRoomReqHandler:
    def __init__(self, rooms, clients, server_config):
        self.rooms = rooms
        self.clients = clients
        self.server_config = server_config

    def handle(self, sender_conn, msg):
        try:
            room_code = generate_unique_code(8, self.rooms)
            room = Room(self.server_config, msg.room_name,
                        msg.user_name, sender_conn)

            resp = messages.CreateRoomResp()
            resp.status = 'OK'
            resp.room_code = room_code

            self.rooms[room_code] = room
            msg_handling.send(sender_conn, resp, self.server_config)

            logging.debug(
                '[CREATE_ROOM_REQ_HANDLER] Created new room with room code {}'.format(room_code))

        except:
            traceback.print_exc()
            logging.error(
                '[CREATE_ROOM_REQ_HANDLER] Error ocured when handling message')
            resp = messages.CreateRoomResp()
            resp.status = 'NOT_OK'
            msg_handling.send(sender_conn, resp, self.server_config)
