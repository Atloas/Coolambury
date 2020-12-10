import logging
import msg_handling
import messages

class ClientConnection:
    def __init__(self, conn, addr, server_config, msg_dispatcher):
        self._server_config = server_config
        self._conn = conn
        self._addr = addr
        self._dispatcher = msg_dispatcher
        self._connected = True
        # TODO: Add time of logging
        logging.debug('[NEW CONNECTION] {} connected'.format(addr))

    def handle_client_messages(self):
        while self._connected:
            msg_name, msg_body = msg_handling.receive(self._conn, self._server_config)
            if msg_body:
                self._dispatcher.dispatch(self._conn, msg_name, msg_body)

    def close_connection(self):
        self._connected = False
        self._conn.close()
