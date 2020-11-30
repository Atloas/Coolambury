import logging
import socket
import threading
import msg_handler
import messages

class Server:
    def __init__(self, config):
        self.config = config
        ADDR = ('', config.PORT)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)

    def handle_client(self, conn, addr):
        logging.debug('[NEW CONNECTION] {} connected'.format(addr))
        connected = True

        while connected:
            received_msg = msg_handler.receive(conn, self.config)
            if received_msg:
                print(received_msg)
                resp = messages.CreateRoomResp()
                resp.status = 'OK'
                resp.room_code = 'Jakis losowy room code hehe'
                msg_handler.send(conn, resp, self.config)

        conn.close()

    def start(self):
        logging.debug('[STARTING] server is starting...')
        self.server.listen()
        print("haha")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            logging.debug('[ACTIVE CONNECTIONS] {}'.format(threading.activeCount() - 1))