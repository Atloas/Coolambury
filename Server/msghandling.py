import logging
import gameroom as gr
import networking as nw
import msgcreation as mc
import traceback

class RoomNotExistsException(Exception):
    pass

def handle_ChatMessageReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()

        room = rooms[msg['room_code']]
        with room.lock:
            room.handle_ChatMessageReq(msg, sender_conn)

    except:
        logging.error(
            '[handle_ChatMessageReq] Room with code {} not found'.format(msg.room_code))


def handle_CreateRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        room_code = mc.generate_unique_code(8, rooms)
        room = gr.Room(msg['user_name'], sender_conn, room_code, resources['words'])

        resp = mc.build_ok_create_room_resp(room_code)
        rooms[room_code] = room
        sender_conn.send(resp)

        logging.debug(
            '[handle_CreateRoomReq] Created new room with room code {}'.format(room_code))

    except:
        logging.error(
            '[handle_CreateRoomReq] Error ocured when handling message {}'.format(msg))

        resp = mc.build_not_ok_create_room_resp()
        sender_conn.send(resp)

def handle_JoinRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()

        room = rooms[msg['room_code']]

        with room.lock:
            room.handle_JoinRoomReq(msg, sender_conn)

    except RoomNotExistsException:
        info = 'Room with code {} not found'.format(msg['room_code'])
        nw.send_NOT_OK_JoinRoomResp_with_info(sender_conn, info)

    except:
        logging.error('[handle_JoinRoomReq] Error occurred when handling message{}'.format(msg))
        nw.send_NOT_OK_JoinRoomResp_with_info(sender_conn, 'Unknown error occurred when joining room!')


def handle_ExitClientReq(resources, sender_conn, msg):
    try:
        code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[code]

        with room.lock:
            room.handle_ExitClientReq(msg, sender_conn)

        if room.num_of_members() == 0:
            del rooms[code]
            logging.info('[handle_ExitClientReq] Room with code {} deleted (0 players)'.format(code))
            
    except:
        logging.error('[handle_ExitClientReq] Error ocured when handling message {}'.format(msg))


def handle_StartGameReq(resources, sender_conn, msg):
    try:
        room_code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[room_code]

        with room.lock:
            room.handle_StartGameReq(msg, sender_conn)
    
    except:
        logging.error('[handle_StartGameReq] Error ocured when handling message {}'.format(msg))
        resp = mc.build_start_game_resp_not_ok()
        sender_conn.send(resp)

def handle_WordSelectionResp(resources, sender_conn, msg):
    try:
        room_code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[room_code]

        with room.lock:
            room.handle_WordSelectionResp(msg)
    
    except:
        logging.error('[handle_WordSelectionResp] Unknown error occurred when handling message {}'.format(msg))
    
def handle_DrawStrokeReq(resources, sender_conn, msg):
    try:
        room_code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[room_code]

        with room.lock:
            room.handle_DrawStrokeReq(msg)

    except:
        logging.error('[handle_DrawStrokeReq] Unknown error occurred when handling message {}'.format(msg))
        
def handle_UndoLastStrokeReq(resources, sender_conn, msg):
    try:
        room_code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[room_code]

        with room.lock:
            room.handle_UndoLastStrokeReq(msg)

    except:
        logging.error('[handle_UndoLastStrokeReq] Unknown error occurred when handling message {}'.format(msg))

def handle_ClearCanvasReq(resources, sender_conn, msg):
    try:
        room_code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[room_code]

        with room.lock:
            room.handle_ClearCanvasReq(msg)

    except:
        logging.error('[handle_ClearCanvasReq] Unknown error occurred when handling message {}'.format(msg))