import logging
import socket
import threading
import msg_handling
import messages
from clientconnection import ClientConnection

class Server:
    def __init__(self, config):
        self.config = config
        ADDR = ('', config.PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(ADDR)

        self.connected_clients = []
        self.connected_clients_lock = threading.Lock()

        self.rooms = {}

        logging.debug('[INITIALIZING SERVER]')


    def start(self):
        logging.debug('[STARTING] server is starting...')
        self.server_socket.listen()

        while True:
            conn, addr = self.server_socket.accept()

            with self.connected_clients_lock:
                new_client = ClientConnection(conn, addr, self.config)
                self.connected_clients.append(new_client)
                thread = threading.Thread(target=new_client.handle_client_messages)
                thread.start()

            logging.debug('[ACTIVE CONNECTIONS] {}'.format(threading.activeCount() - 1))
