import logging
import threading
import sys
import json
import msghandling as mh
import networking as nw

class Server:
    def __init__(self):
        self._load_config_file()
        self._server_socket = nw.create_and_bind_socket(self._config)
        self._connected_clients = []
        self._rooms = {}
        self._message_dispatcher = mh.MessageDispatcher()
        self._register_dispatcher_handlers()
        logging.debug('[INITIALIZING SERVER]')

    def _load_config_file(self):
        try:
            config_path = sys.argv[1]
            with open(config_path, 'r') as config_file:
                self._config = json.load(config_file)
        except:
            logging.error('Error ocured when loading configuration file!')
            exit()

    def _register_dispatcher_handlers(self):
        self._message_dispatcher.register_handler('CreateRoomReq',
                                                 mh.CreateRoomReqHandler(
                                                     self._rooms,
                                                     self._connected_clients,
                                                     self._config))


        self._message_dispatcher.register_handler('JoinRoomReq',
                                                  mh.JoinRoomReqHandler(
                                                     self._rooms,
                                                     self._connected_clients,
                                                     self._config))

        self._message_dispatcher.register_handler('WriteChatReq',
                                                  mh.ChatMessageReqHandler(
                                                     self._rooms,
                                                     self._connected_clients,
                                                     self._config))

    def start(self):
        logging.debug('[STARTING] server is starting...')
        self._server_socket.listen()

        while True:
            conn, addr = self._server_socket.accept()

            new_client = nw.ClientConnection(conn, addr, self._config, self._message_dispatcher)
            self._connected_clients.append(new_client)
            thread = threading.Thread(target=new_client.handle_client_messages)
            thread.start()

            logging.debug('[ACTIVE CONNECTIONS] {}'.format(threading.activeCount() - 1))

                                                     
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    coolambury_server = Server()
    coolambury_server.start()
    