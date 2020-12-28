import logging
from room import Room
import networking as nw
import msgcreation as mc


class RoomNotExistsException(Exception):
    pass


class UsernameTakenException(Exception):
    pass


def handleChatMessageReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()
        
        room = rooms[msg['room_code']]
        room.add_client(msg['user_name'], sender_conn)
        chat_msg = mc.build_chat_msg_bc(msg['user_name'], msg['message'])
        room.broadcast_chat_message(chat_msg)

    except:
        logging.error(
            '[WRITE_CHAT_REQ_HANDLER] Room of code {} not registered on the server'.format(msg.room_code))


def handleCreateRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        room_code = mc.generate_unique_code(8, rooms)
        room = Room(resources['config'], msg['user_name'], sender_conn)

        resp = mc.build_ok_create_room_resp(room_code)
        rooms[room_code] = room
        nw.send(sender_conn, resp, resources['config'])

        logging.debug(
            '[CREATE_ROOM_REQ_HANDLER] Created new room with room code {}'.format(room_code))

    except:
        logging.error(
            '[CREATE_ROOM_REQ_HANDLER] Error ocured when handling message {}'.format(msg))

        resp = mc.build_not_ok_create_room_resp()
        nw.send(sender_conn, resp, resources['config'])


def handleJoinRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()
        
        room = rooms[msg['room_code']]

        if msg['user_name'] in room._joined_clients:
            raise UsernameTakenException()

        room.add_client(msg['user_name'], sender_conn)
        resp = mc.build_ok_join_room_resp()
        nw.send(sender_conn, resp, resources['config'])
        join_notification = mc.build_join_notification(msg['user_name'])
        room.broadcast_chat_message(join_notification)

        logging.debug('[JOIN_ROOM_REQ_HANDLER] User {} joined to room {}'.format(
            msg['user_name'], msg['room_code']))

    except:
        logging.error(
            '[JOIN_ROOM_REQ_HANDLER] Error ocured when handling message{}'.format(msg))

        resp = mc.build_not_ok_join_room_resp()
        nw.send(sender_conn, resp, resources['config'])
