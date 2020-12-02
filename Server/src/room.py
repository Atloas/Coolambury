import msg_handling

class Room:
    def __init__(self, server_config, room_name, owner_name, owner_connection):
        pass
        self.server_config = server_config
        self.room_name = room_name
        self.owner = (owner_name, owner_connection)
        self.joined_clients = {owner_name : owner_connection}

    # def broadcast_chat_message(self, msg):
    #     for client in self.joined_clients.items():
    #         msg_handling.send(client, msg, self.server_config)
