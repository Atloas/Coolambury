import pickle
import config
import messages


def send(conn, msg_body, config):
    msg_body_bytes = pickle.dumps(msg_body)
    msg_header = messages.MessageHeader(len(msg_body_bytes), type(msg_body).__name__)
    msg_header_bytes = pickle.dumps(msg_header)
    msg_header_string_len = len(msg_header_bytes)

    msg_header_bytes += b' ' * (config.HEADER_LEN - msg_header_string_len)

    conn.send(msg_header_bytes)
    conn.send(msg_body_bytes)

def receive(conn, config):
    msg_header_bytes = conn.recv(config.HEADER_LEN)
    if msg_header_bytes != b'':
        msg_header = pickle.loads(msg_header_bytes)
        msg_body_bytes = conn.recv(msg_header.length)
        msg_body = pickle.loads(msg_body_bytes)

        return msg_body


        
