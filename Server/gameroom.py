import networking as nw
import msgcreation as mc
from enum import Enum
import random
import logging
import threading

class GameAlreadyStartedException(Exception):
    pass

class StartedNotByOwnerException(Exception):
    pass

class NotEnaughPlayersException(Exception):
    pass

class UsernameTakenException(Exception):
    pass

class StateErrorException(Exception):
    pass

class RoomState(Enum):
    PREGAME = 0
    STARTING_GAME = 1
    WORD_SELECTION = 2
    DRAWING = 3
    POSTGAME = 4

class Room:
    def __init__(self, owner_name, owner_connection, room_code):
        self._owner = owner_name
        self._joined_clients = {owner_name : owner_connection}
        self._room_code = room_code
        self._state = RoomState.PREGAME
        self.lock = threading.Lock()

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
            try:
                client[1].send(msg)
            except:
                logging.warn('[ROOM ({})] Unable to send message {} to {}!'.format(self._room_code, msg['msg_name'], client[0]))

    def start_game(self, user_name):
        if user_name != self._owner:
            raise StartedNotByOwnerException()

        if self._state != RoomState.PREGAME:
            raise StateErrorException()

        if self.num_of_members() < 2:
            raise NotEnaughPlayersException()

        logging.info('[ROOM ({})] Attempting to start a game!'.format(self._room_code))
        self._state = RoomState.STARTING_GAME

        self._drawing_queue = list(self._joined_clients.keys())
        random.shuffle(self._drawing_queue)
    
    def enter_word_selection_state(self):
        logging.info('[ROOM ({})] Entering WORD_SELECTION state!'.format(self._room_code))
        self._state = RoomState.WORD_SELECTION
        words = ['cat', 'dog', 'apple', 'car', 'smartphone', 'python'] # TODO : this is temporary solution!

        words_to_select = random.sample(words, 3)

        self._current_word = None
        self._artist = self._drawing_queue[0]
        del self._drawing_queue[0]
        self._drawing_queue.append(self._artist)
        
        logging.debug('[ROOM ({})] Word draw result for artist {} : {}!'.format(self._room_code, self._artist, words_to_select))

        return words_to_select
    
    def _announce_word_guessed(self, msg):
        word_guessed_bc = {
            'msg_name': 'WordGuessedBc',
            'user_name': msg['user_name'],
            'word': self._current_word, 
            'score_awarded': {player[0]: 0 for player in self._joined_clients.items()}
        }
        
        self.broadcast_message(word_guessed_bc)

        words_to_select = self.enter_word_selection_state()

        artist_pick_bc = {
            'msg_name': 'ArtistPickBc',
            'artist': self._artist
        }
        self.broadcast_message(artist_pick_bc)
        self.send_words_to_select_to_artist(words_to_select)



    def handle_ChatMessageReq(self, msg, sender_conn):
        if self._state == RoomState.DRAWING:
            if msg['message'] == self._current_word:
                self._announce_word_guessed(msg)
        else:
            chat_msg = mc.build_chat_msg_bc(msg['user_name'], msg['message'])
            self.broadcast_message(chat_msg)

    def handle_JoinRoomReq(self, msg, sender_conn):
        try:
            if msg['user_name'] in self._joined_clients:
                raise UsernameTakenException()

            self.add_client(msg['user_name'], sender_conn)
            resp = mc.build_ok_join_room_resp()
            sender_conn.send(resp)
            join_notification = mc.build_join_notification(msg['user_name'])
            self.broadcast_message(join_notification)

            logging.debug('[ROOM ({})] User {} joined'.format(self._room_code, msg['user_name']))

        except GameAlreadyStartedException:
            info = 'Game already started!'
            nw.send_NOT_OK_JoinRoomResp_with_info(sender_conn, info)

        except UsernameTakenException:
            info = 'Username {} already taken in room with code {}'.format(msg['user_name'], msg['room_code'])
            nw.send_NOT_OK_JoinRoomResp_with_info(sender_conn, info)
        
    def handle_ExitClientReq(self, msg, sender_conn):
        user_name = msg['user_name']
        removed = self.remove_client_by_name_if_exists(user_name)

        if removed:
            leave_notification = mc.build_leave_notification(user_name)
            self.broadcast_message(leave_notification)

            logging.info('[ROOM ({})] Removed user {}'.format(self._room_code, user_name))
        else:
            logging.info('[ROOM ({})] User {} not found'.format(self._room_code, user_name))

    def send_words_to_select_to_artist(self, words_to_select):
        self._state = RoomState.WORD_SELECTION
        word_selection_req = mc.build_word_selection_req(self._artist, self._room_code, words_to_select)
        artist_connection = self._joined_clients[self._artist]
        artist_connection.send(word_selection_req)

    def handle_StartGameReq(self, msg, sender_conn):
        try:
            user_name = msg['user_name']
            self.start_game(user_name)
            resp = mc.build_start_game_resp_ok()
            sender_conn.send(resp)

            words_to_select = self.enter_word_selection_state()

            start_game_bc = {'msg_name': 'StartGameBc', 'artist': self._artist}
            self.broadcast_message(start_game_bc)
            self.send_words_to_select_to_artist(words_to_select)

        except StartedNotByOwnerException:
            resp = mc.build_start_game_resp_not_ok('Only room owner can start the game!')
            sender_conn.send(resp)
        
        except StateErrorException:
            resp = mc.build_start_game_resp_not_ok('Trying to start game not in PREGAME state')
            sender_conn.send(resp)
    
        except NotEnaughPlayersException:
            resp = mc.build_start_game_resp_not_ok('There must be at least 2 players to start the game!')
            sender_conn.send(resp)

    def handle_WordSelectionResp(self, msg):
        try:
            if self._state != RoomState.WORD_SELECTION:
                raise StateErrorException()

            self._state = RoomState.DRAWING
            self._current_word = msg['selected_word']

        except StateErrorException:
            logging.warn('[ROOM ({})] Received WordSelectionResp from {} not in state WORD_SELECTION'.format(self._room_code, msg['user_name']))
        

    def handle_DrawStrokeReq(self, msg):
        try:
            if self._state != RoomState.DRAWING:
                raise StateErrorException()

            draw_stroke_bc = {
                'msg_name': 'DrawStrokeBc',
                'stroke_coordinates': msg['stroke_coordinates']
            }
            self.broadcast_message(draw_stroke_bc)
            
        except StateErrorException:
            logging.warn('[ROOM ({})] Received WordSelectionResp from {} not in state DRAWING'.format(self._room_code, msg['user_name']))
        
        except:
            logging.error('[ROOM ({})] Unknown error occurred when handling message {}'.format(self._room_code, msg))

    def handle_UndoLastStrokeReq(self, msg):
        try:
            if self._state != RoomState.DRAWING:
                raise StateErrorException()

            undo_last_stroke_bc = {'msg_name': 'UndoLastStrokeBc'}
            self.broadcast_message(undo_last_stroke_bc)

        except StateErrorException:
            logging.warn('[ROOM ({})] Received UndoLastStrokeReq from {} not in state DRAWING'.format(self._room_code, msg['user_name']))
        
        except:
            logging.error('[ROOM ({})] Unknown error occurred when handling message {}'.format(self._room_code, msg))
    
    def handle_ClearCanvasReq(self, msg):
        try:
            if self._state != RoomState.DRAWING:
                raise StateErrorException()

            clear_canvas_bc = {'msg_name': 'ClearCanvasBc'}
            self.broadcast_message(clear_canvas_bc)

        except StateErrorException:
            logging.warn('[ROOM ({})] Received ClearCanvasReq from {} not in state DRAWING'.format(self._room_code, msg['user_name']))
        
        except:
            logging.error('[ROOM ({})] Unknown error occurred when handling message {}'.format(self._room_code, msg))
            