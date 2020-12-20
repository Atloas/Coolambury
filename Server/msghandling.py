import logging
from room import Room
import networking as nw
import msgcreation as mc


class RoomNotExistsException(Exception):
    pass


class UsernameTakenException(Exception):
    pass


class BaseHandler:
    def __init__(self, rooms, clients, server_config):
        self._rooms = rooms
        self._clients = clients
        self._server_config = server_config


class ChatMessageReqHandler(BaseHandler):
    def __init__(self, rooms, clients, server_config):
        super().__init__(rooms, clients, server_config)

    def handle(self, sender_conn, msg):
        try:
            if msg['room_code'] not in self._rooms:
                raise RoomNotExistsException()
            
            room = self._rooms[msg['room_code']]
            room.add_client(msg['user_name'], sender_conn)
            chat_msg = mc.build_chat_msg_bc(msg['user_name'], msg['message'])
            room.broadcast_chat_message(chat_msg)

        except:
            logging.error(
                '[WRITE_CHAT_REQ_HANDLER] Room of code {} not registered on the server'.format(msg.room_code))


class CreateRoomReqHandler(BaseHandler):
    def __init__(self, rooms, clients, server_config):
        super().__init__(rooms, clients, server_config)

    def handle(self, sender_conn, msg):
        try:
            room_code = mc.generate_unique_code(8, self._rooms)
            room = Room(self._server_config, msg['user_name'], sender_conn)
            resp = mc.build_ok_create_room_resp(room_code)
            self._rooms[room_code] = room
            nw.send(sender_conn, resp, self._server_config)

            logging.debug(
                '[CREATE_ROOM_REQ_HANDLER] Created new room with room code {}'.format(room_code))

        except:
            logging.error(
                '[CREATE_ROOM_REQ_HANDLER] Error ocured when handling message {}'.format(msg))

            resp = mc.build_not_ok_create_room_resp()
            nw.send(sender_conn, resp, self._server_config)


class JoinRoomReqHandler(BaseHandler):
    def __init__(self, rooms, clients, server_config):
        super().__init__(rooms, clients, server_config)

    def handle(self, sender_conn, msg):
        try:
            if msg['room_code'] not in self._rooms:
                raise RoomNotExistsException()
            
            room = self._rooms[msg['room_code']]

            if msg['user_name'] in room._joined_clients:
                raise UsernameTakenException()

            room.add_client(msg['user_name'], sender_conn)
            resp = mc.build_ok_join_room_resp()
            nw.send(sender_conn, resp, self._server_config)
            join_notification = mc.build_join_notification(msg['user_name'])
            room.broadcast_chat_message(join_notification)

            logging.debug('[JOIN_ROOM_REQ_HANDLER] User {} joined to room {}'.format(
                msg['user_name'], msg['room_code']))

        except:
            logging.error(
                '[JOIN_ROOM_REQ_HANDLER] Error ocured when handling message{}'.format(msg))

            resp = mc.build_not_ok_join_room_resp()
            nw.send(sender_conn, resp, self._server_config)


class MessageDispatcher:
    def __init__(self):
        self._registered_handlers = {}

    def dispatch(self, conn, msg_name, msg_body):
        logging.debug('[DISPATCHER] dispatching message {}'.format(msg_name))
        try:
            handler = self._registered_handlers[msg_name]
            handler.handle(conn, msg_body)
        except:
            logging.error('An error ocured when handling {} = {}'.format(msg_name, msg_body))

    def register_handler(self, message_name, message_handler):
        self._registered_handlers[message_name] = message_handler
        logging.debug('[DISPATCHER] : registered handler for {}'.format(message_name))
        