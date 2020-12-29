import logging
import gameroom as gr
import networking as nw
import msgcreation as mc

class RoomNotExistsException(Exception):
    pass


class UsernameTakenException(Exception):
    pass

def handle_ChatMessageReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()
        
        room = rooms[msg['room_code']]
        room.add_client(msg['user_name'], sender_conn)
        chat_msg = mc.build_chat_msg_bc(msg['user_name'], msg['message'])
        room.broadcast_message(chat_msg)

    except:
        logging.error(
            '[handle_ChatMessageReq] Room with code {} not found'.format(msg.room_code))


def handle_CreateRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        room_code = mc.generate_unique_code(8, rooms)
        room = gr.Room(resources['config'], msg['user_name'], sender_conn, room_code)

        resp = mc.build_ok_create_room_resp(room_code)
        rooms[room_code] = room
        nw.send(sender_conn, resp, resources['config'])

        logging.debug(
            '[handle_CreateRoomReq] Created new room with room code {}'.format(room_code))

    except:
        logging.error(
            '[handle_CreateRoomReq] Error ocured when handling message {}'.format(msg))

        resp = mc.build_not_ok_create_room_resp()
        nw.send(sender_conn, resp, resources['config'])

def send_NOT_OK_JoinRoomResp_with_info(conn, config, info):
    logging.debug('[handle_JoinRoomReq] {}'.format(info))
    resp = mc.build_not_ok_join_room_resp(info=info)
    nw.send(conn, resp, config)

def handle_JoinRoomReq(resources, sender_conn, msg):
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
        room.broadcast_message(join_notification)

        logging.debug('[handle_JoinRoomReq] User {} joined to room {}'.format(
            msg['user_name'], msg['room_code']))

    except gr.GameAlreadyStartedException:
        info = 'Game already started!'
        send_NOT_OK_JoinRoomResp_with_info(sender_conn, resources['config'], info)

    except RoomNotExistsException:
        info = 'Room with code {} not found'.format(msg['room_code'])
        send_NOT_OK_JoinRoomResp_with_info(sender_conn, resources['config'], info)

    except UsernameTakenException:
        info = 'Username {} already taken in room with code {}'.format(msg['user_name'], msg['room_code'])
        send_NOT_OK_JoinRoomResp_with_info(sender_conn, resources['config'], info)

    except:
        logging.error('[handle_JoinRoomReq] Error occurred when handling message{}'.format(msg))
        resp = mc.build_not_ok_join_room_resp()
        nw.send(sender_conn, resp, resources['config'])


def handle_ExitClientReq(resources, sender_conn, msg):
    try:
        user_name = msg['user_name']
        code = msg['room_code']

        rooms = resources['rooms']
        room = rooms[code]
        removed = room.remove_client_by_name_if_exists(user_name)

        if removed:
            leave_notification = mc.build_leave_notification(user_name)
            room.broadcast_message(leave_notification)
            logging.info('[handle_ExitClientReq] Removed {} from room with code {}'.format(user_name, code))
        else:
            logging.info('[handle_ExitClientReq] User {} not found in room with code {}'.format(user_name, code))
        
        if room.num_of_members() == 0:
            del rooms[code]
            logging.info('[handle_ExitClientReq] Room with code {} deleted (0 players)'.format(code))
    except:
        logging.error('[handle_ExitClientReq] Error ocured when handling message {}'.format(msg))


def handle_StartGameReq(resources, sender_conn, msg):
    try:
        user_name = msg['user_name']
        room_code = msg['room_code']

        rooms = resources['rooms']
        room = rooms[room_code]
        room.start_game(user_name)

        resp = mc.build_start_game_resp_ok()
        nw.send(sender_conn, resp, resources['config'])
        start_game_bc = {'msg_name': 'StartGameBc'}
        room.broadcast_message(start_game_bc)
        # TODO: Start PROMPT_SELECTION
    except gr.StartedNotByOwnerException:
        resp = mc.build_start_game_resp_not_ok('Only room owner can start game!')
        nw.send(sender_conn, resp, resources['config'])
    
    except gr.NotEnaughPlayersException:
        resp = mc.build_start_game_resp_not_ok('There must be at least 2 players to start the game!')
        nw.send(sender_conn, resp, resources['config'])
    
    except:
        logging.error('[handle_StartGameReq] Error ocured when handling message {}'.format(msg))
        resp = mc.build_start_game_resp_not_ok()
        nw.send(sender_conn, resp, resources['config'])
