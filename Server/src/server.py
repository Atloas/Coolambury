import logging
import socket
import threading
import msg_handling

from clientconnection import ClientConnection
from messagedispatcher import MessageDispatcher
from messagehandlers import *

class Server:
    def __init__(self, config):
        self.config = config
        ADDR = ('', config.PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(ADDR)
        self.connected_clients = []
        self.rooms = {}
        self.message_dispatcher = MessageDispatcher()
        self._register_dispatcher_handlers()
        logging.debug('[INITIALIZING SERVER]')

    def start(self):
        logging.debug('[STARTING] server is starting...')
        self.server_socket.listen()

        while True:
            conn, addr = self.server_socket.accept()

            new_client = ClientConnection(conn, addr, self.config, self.message_dispatcher)
            self.connected_clients.append(new_client)
            thread = threading.Thread(target=new_client.handle_client_messages)
            thread.start()

            logging.debug('[ACTIVE CONNECTIONS] {}'.format(threading.activeCount() - 1))

    def _register_dispatcher_handlers(self):
        self.message_dispatcher.register_handler('CreateRoomReq',
                                                 CreateRoomReqHandler(
                                                     self.rooms,
                                                     self.connected_clients,
                                                     self.config))
