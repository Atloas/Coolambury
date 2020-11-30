import pickle
import config
import messages


def receive(conn, config):
    msg_header_bytes = conn.recv(config.HEADER_LEN)
    if msg_header_bytes != b'':
        msg_header = pickle.loads(msg_header_bytes)

        msg_body_bytes = conn.recv(msg_header.length)

        msg_body = pickle.loads(msg_body_bytes)

        print(msg_body.username)
        print(msg_body.roomname)


    # msg_len = conn.recv(config.HEADER_LEN).decode(config.FORMAT)
    # if msg_len:
    #     msg_len = int(msg_len)
    #     msg = conn.recv(msg_len).decode(config.FORMAT)
    #     logging.info('[MESSAGE RECEIVED] from: {} | msg: {}'.format(addr, msg))
    #     if msg == config.DISCONNECT_MSG:
    #         connected = False

    #     conn.send('Hello from server!'.encode(config.FORMAT))
