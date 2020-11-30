import socket
import threading
import logging


import common
import config
import msg_handler


config = config.Config()
ADDR = ('', config.PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    logging.debug('[NEW CONNECTION] {} connected'.format(addr))
    connected = True

    while connected:
        msg_handler.receive(conn, config)

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
    logging.basicConfig(filename='Server/logs/server.log', filemode='w', level=logging.DEBUG)
    start()
