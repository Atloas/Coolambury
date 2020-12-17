import logging

class MessageDispatcher:
    def __init__(self):
        self._registered_handlers = {}

    def dispatch(self, conn, msg_name, msg_body):
        logging.debug('[DISPATCHER] dispatching message {}'.format(msg_name))
        try:
            handler = self._registered_handlers[msg_name]
            handler.handle(conn, msg_body)
        except:
            logging.error('An error ocured when handling {} = {}'.format(msg_name, msg_body))

    def register_handler(self, message_name, message_handler):
        self._registered_handlers[message_name] = message_handler
        logging.debug('[DISPATCHER] : registered handler for {}'.format(message_name))

