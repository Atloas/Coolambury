import socket
import threading
import logging

class Config:
    def __init__(self):
        self.PORT = 5050
        self.HEADER_LEN = 64
        # self.SERVER = '172.104.225.26'
        self.SERVER = 'localhost'
        self.DISCONNECT_MSG = '!DISCONNECT'


ADDR = ('', PORT)
FORMAT = 'utf-8'
print(SERVER)

print(socket.gethostname())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    logging.debug('[NEW CONNECTION] {} connected'.format(addr))
    connected = True

    while connected:
        msg_len = conn.recv(HEADER_LEN).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode(FORMAT)
            logging.info('[MESSAGE RECEIVED] from: {} | msg: {}'.format(addr, msg))
            if msg == DISCONNECT_MSG:
                connected = False

            conn.send('Hello from server!'.encode(FORMAT))

    conn.close()


def start():
    logging.debug('[STARTING] server is starting...')
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        logging.debug('[ACTIVE CONNECTIONS] {}'.format(threading.activeCount() - 1))



if __name__ == '__main__':
    logging.basicConfig(filename='logs/server.log', filemode='w', level=logging.DEBUG)
    start()
