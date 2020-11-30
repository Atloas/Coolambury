import pickle
import config
import messages


def send(client, msg_body, config):

    msg_body_bytes = pickle.dumps(msg_body)
    msg_header = messages.MessageHeader(len(msg_body_bytes), type(msg_body).__name__)
    msg_header_bytes = pickle.dumps(msg_header)
    msg_header_string_len = len(msg_header_bytes)

    msg_header_bytes += b' ' * (config.HEADER_LEN - msg_header_string_len)

    client.send(msg_header_bytes)
    client.send(msg_body_bytes)


