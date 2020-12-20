import unittest
from unittest.mock import Mock
from unittest.mock import patch
from Application.GameWindow import GameWindow
from Communication.ConnectionHandler import ConnectionHandler
import Communication.SocketMsgHandler
from PyQt5.QtWidgets import QApplication
import sys

# for UT:
# $env:PYTHONPATH = ".\Client\"

app = QApplication(sys.argv)


class TestGameWindow(unittest.TestCase):

    connHandlerMock = Mock(spec=ConnectionHandler)
    clientContextDummy = {}
    clientContextDummy['username'] = 'username'
    clientContextDummy['roomCode'] = 'abcdefgh'

    @classmethod
    def setUp(self):
        self.sut = GameWindow(self.clientContextDummy, self.connHandlerMock)
        self.initialGameRoomIdMessage = 'GAME ROOM ID: {}\n'.format(
            self.clientContextDummy['roomCode'])

    @classmethod
    def tearDown(self):
        pass

    def test_shouldDisplayGameRoomIdAfterWindowOpened(self):
        self.assertEqual(self.sut.chat.toPlainText(), self.initialGameRoomIdMessage)

    def test_shouldProperlyDisplayUserMsgInChatAndClearChatEntryLine(self):
        self.test_shouldDisplayGameRoomIdAfterWindowOpened()
        
        messageContent = '{}: {}'.format(
            self.sut.clientContext['username'], 'Hej byczq')
        clearedChatEntry = ''
        self.sut.chatEntryLine.setText(messageContent)
        self.sut.display_user_msg(messageContent)

        self.assertEqual(self.sut.chatEntryLine.text(), clearedChatEntry
        self.assertEqual(self.sut.chat.toPlainText(), '{}{}{}'.format(
            self.initialGameRoomIdMessage, messageContent, '\n'))


if __name__ == '__main__':
    unittest.main()
