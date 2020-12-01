import logging
import msg_handling
import messages

class ClientConnection:
    def __init__(self, conn, addr, server_config):
        self.server_config = server_config
        self.conn = conn
        self.addr = addr
        self.connected = True
        logging.debug('[NEW CONNECTION] {} connected'.format(addr))

    def handle_client_messages(self):
        while self.connected:
            received_msg = msg_handling.receive(self.conn, self.server_config)
            if received_msg:
                print(received_msg)
                resp = messages.CreateRoomResp()
                resp.status = 'OK'
                resp.room_code = 'Jakis losowy room code hehe'
                msg_handling.send(self.conn, resp, self.server_config)

    def close_connection(self):
        self.connected = False
        self.conn.close()
