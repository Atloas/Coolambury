import networking as nw
from enum import Enum
import random
import logging

class GameAlreadyStartedException(Exception):
    pass

class StartedNotByOwnerException(Exception):
    pass

class NotEnaughPlayersException(Exception):
    pass

class RoomState(Enum):
    PREGAME = 0
    STARTING_GAME = 1
    PROMPT_SELECTION = 2
    DRAWING = 3
    POSTGAME = 4

class Room:
    def __init__(self, server_config, owner_name, owner_connection, room_code): 
        self._server_config = server_config
        self._owner = owner_name
        self._joined_clients = {owner_name : owner_connection}
        self._room_code = room_code
        self._state = RoomState.PREGAME

    def get_current_state(self):
        return self._state

    def num_of_members(self):
        return len(self._joined_clients)

    def add_client(self, user_name, user_conn):
        if self._state not in [RoomState.PREGAME, RoomState.POSTGAME]:
            raise GameAlreadyStartedException()
        self._joined_clients[user_name] = user_conn
    
    def remove_client_by_name_if_exists(self, user_name):
        try:
            del self._joined_clients[user_name]
            return True
        except:
            return False

    def remove_client_by_connection_if_exists(self, user_conn):
        for user_name, value in self._joined_clients.items():
            if value == user_conn:
                removed = self.remove_client_by_name_if_exists(user_name)
                return removed

    def broadcast_message(self, msg):
        for client in self._joined_clients.items():
            nw.send(client[1], msg, self._server_config)

    def start_game(self, user_name):
        if user_name != self._owner:
            raise StartedNotByOwnerException()

        if self.num_of_members() < 2:
            raise NotEnaughPlayersException()

        logging.info('[ROOM ({})] Attempting to start a game!')
        self._state = RoomState.STARTING_GAME

        self._drawing_queue = self._joined_clients.keys()
        random.shuffle(self._drawing_queue)
        