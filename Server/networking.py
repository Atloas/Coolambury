import logging
import msghandling as mh
import pickle
import socket

def send(conn, msg_body, config):
    msg_body_bytes = pickle.dumps(msg_body)
    msg_header = {'length': len(msg_body_bytes), 'name': msg_body['msg_name']}
    msg_header_bytes = pickle.dumps(msg_header)
    msg_header_string_len = len(msg_header_bytes)

    msg_header_bytes += b' ' * (config['HEADER_LEN'] - msg_header_string_len)

    conn.send(msg_header_bytes)
    conn.send(msg_body_bytes)

def receive(conn, config):
    msg_header_bytes = conn.recv(config['HEADER_LEN'])
    if msg_header_bytes != b'':
        msg_header = pickle.loads(msg_header_bytes)
        msg_body_bytes = conn.recv(msg_header['length'])
        msg_body = pickle.loads(msg_body_bytes)

        return (msg_header['name'], msg_body)

    return ('', None)

def create_and_bind_socket(config):
        ADDR = ('', config['PORT'])
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(ADDR)

        return server_socket


class ClientConnection:
    def __init__(self, conn, addr, resources, msg_mapping):
        self._resources = resources
        self._conn = conn
        self._addr = addr
        self._msg_mapping = msg_mapping
        self._connected = True
        # TODO: Add time of logging
        logging.debug('[NETWORKING] {} connected'.format(addr))

    def handle_client_messages(self):
        while self._connected:
            msg_name, msg_body = receive(self._conn, self._resources['config'])
            if msg_body:
                logging.debug('[NETWORKING] dispatching message {}'.format(msg_body))
                try:
                    handling_func = self._msg_mapping[msg_name]
                    handling_func(self._resources, self._conn, msg_body)
                except KeyError:
                    logging.error('[NETWORKING] Handlind function not found for {}'.format(msg_name))
                except:
                    logging.error('[NETWORKING] Unknown error occurred when handling msg {} = {}'.format(msg_name, msg_body))


    def close_connection(self):
        try:
            self._connected = False
            self._conn.shutdown(socket.SHUT_RDWR)
            self._conn.close()
        except:
            logging.error('[CLIENT CONNECTION] Unsuccessful socket shutdown!')

        logging.debug('[CLIENT CONNECTION] Closing connection')
