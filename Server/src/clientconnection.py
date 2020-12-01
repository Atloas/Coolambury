import logging
import msg_handling
import messages

class ClientConnection:
    def __init__(self, conn, addr, server_config, msg_dispatcher):
        self.server_config = server_config
        self.conn = conn
        self.addr = addr
        self.dispatcher = msg_dispatcher
        self.connected = True
        logging.debug('[NEW CONNECTION] {} connected'.format(addr))

    def handle_client_messages(self):
        while self.connected:
            msg_name, msg_body = msg_handling.receive(self.conn, self.server_config)
            if msg_body:
                self.dispatcher.dispatch(self.conn, msg_name, msg_body)

    def close_connection(self):
        self.connected = False
        self.conn.close()
