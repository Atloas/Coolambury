import msg_handling

class Room:
    def __init__(self, server_config, owner_name, owner_connection): 
        self._server_config = server_config
        self._owner = (owner_name, owner_connection)
        self._joined_clients = {owner_name : owner_connection}

    def add_client(self, user_name, user_conn):
        self._joined_clients[user_name] = user_conn

    def broadcast_chat_message(self, msg):
        for client in self._joined_clients.items():
            msg_handling.send(client[1], msg, self._server_config)
