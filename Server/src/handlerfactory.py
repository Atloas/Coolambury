import logging

class HandlerFactory:
    def __init__(self, rooms, clients, config):
        self.rooms = rooms
        self.clients = clients
        self.config = config

    def create_handler(self, conn, msg_name):
        logging.debug('[HandlerFactory] creating handler for {}'.format(msg_name))
        # TODO: zrobic tu jakies tworzenie odpowiednich handlerow 
        return None