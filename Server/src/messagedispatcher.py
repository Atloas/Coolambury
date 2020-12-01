import logging
from handlerfactory import HandlerFactory

class MessageDispatcher:
    def __init__(self, rooms, clients, config):
        self._handler_factory = HandlerFactory(rooms, clients, config)

    def dispatch(self, conn, msg_name, msg_body):
        logging.debug('[DISPATCHER] dispatching message {} containing: {}'.format(msg_name, msg_body))
        try:
            _handler = self._handler_factory.create_handler(conn, msg_name)
            _handler.handle(msg_body)
        except:
            logging.error('An error ocured when handling {} = {}'.format(msg_name, msg_body))

