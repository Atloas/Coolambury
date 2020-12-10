import msg_handling
import logging
import messages
from room import Room
import random
import string
import traceback


class RoomNotExistsException(Exception):
    pass

class WriteChatReqHandler:
    def __init__(self, rooms, clients, server_config):
        self._rooms = rooms
        self._clients = clients
        self._server_config = server_config

    def handle(self, sender_conn, msg):
        try:
            if msg.room_code not in self._rooms:
                raise RoomNotExistsException()
            
            room = self._rooms[msg.room_code]

            room.add_client(msg.user_name, sender_conn)

            chat_msg = messages.NewChatMessage()
            chat_msg.author = msg.user_name
            chat_msg.message = msg.message

            room.broadcast_chat_message(chat_msg)

        except:
            traceback.print_exc()
            logging.error(
                '[WRITE_CHAT_REQ_HANDLER] Room of code {} not registered on the server'.format(msg.room_code))

