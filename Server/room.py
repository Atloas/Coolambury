import networking as nw

class Room:
    def __init__(self, server_config, owner_name, owner_connection): 
        self._server_config = server_config
        self._owner = owner_name
        self._joined_clients = {owner_name : owner_connection}

    def num_of_members(self):
        return len(self._joined_clients)

    def add_client(self, user_name, user_conn):
        self._joined_clients[user_name] = user_conn
    
    def remove_client_by_name_if_exists(self, user_name):
        try:
            del self._joined_clients[user_name]
            return True
        except:
            return False

    def remove_client_by_connection_if_exists(self, user_conn):
        for user_name, value in self._joined_clients.items():
            if value == user_conn:
                removed = self.remove_client_by_name_if_exists(user_name)
                return removed

    def broadcast_chat_message(self, msg):
        for client in self._joined_clients.items():
            nw.send(client[1], msg, self._server_config)
