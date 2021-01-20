import pytest
# TODO: Replace unittest.mock with PyTestMock
from unittest.mock import Mock
from Application.GameWindow import GameWindow
from Communication.ConnectionHandler import ConnectionHandler


# for UT on windows(PowerShell):
# $env:PYTHONPATH = ".\Client\"
#
# pytest .\Client\Tests\


@pytest.fixture
def gameWindowFixutre(qtbot):
    connHandlerMock = Mock(spec=ConnectionHandler)
    clientContextDummy = {}
    clientContextDummy['username'] = 'test_user'
    clientContextDummy['roomCode'] = 'abcdefgh'
    sut = GameWindow(clientContextDummy, connHandlerMock)
    qtbot.addWidget(sut)
    pytest.initialGameRoomIdMessage = 'GAME ROOM ID: {}'.format(
        clientContextDummy['roomCode'])
    return sut


def test_should_display_game_room_id_after_window_opened(gameWindowFixutre, qtbot):
    assert gameWindowFixutre.chat.toPlainText() == pytest.initialGameRoomIdMessage


def test_should_properly_display_user_msg_in_chat_and_clear_chat_entry_line(gameWindowFixutre, qtbot):
    test_should_display_game_room_id_after_window_opened(
        gameWindowFixutre, qtbot)
    pytest.initialGameRoomIdMessage = 'GAME ROOM ID: {}'.format(
        gameWindowFixutre.clientContext['roomCode'])

    message_content = {
        'author': gameWindowFixutre.clientContext['username'],
        'message': 'Hello Everybody'
    }
    message_test = '{}: {}'.format(
        message_content['author'], message_content['message'])
    cleared_chat_entry = ''
    gameWindowFixutre.chatEntryLine.setText(message_test)
    gameWindowFixutre.display_message(message_content)

    assert gameWindowFixutre.chatEntryLine.text() == cleared_chat_entry

    actual_chat_contents_after_first_chat_msg = ('{}\n{}'.format(
        pytest.initialGameRoomIdMessage, message_test))

    assert gameWindowFixutre.chat.toPlainText()  == actual_chat_contents_after_first_chat_msg


# class TestGameWindow(unittest.TestCase):

#     connHandlerMock = Mock(spec=ConnectionHandler)
#     clientContextDummy = {}
#     clientContextDummy['username'] = 'username'
#     clientContextDummy['roomCode'] = 'abcdefgh'

#     @classmethod
#     def setUp(self):
#         self.sut = GameWindow(self.clientContextDummy, self.connHandlerMock)
#         self.initialGameRoomIdMessage = 'GAME ROOM ID: {}\n'.format(
#             self.clientContextDummy['roomCode'])

#     @classmethod
#     def tearDown(self):
#         pass

#     def test_shouldDisplayGameRoomIdAfterWindowOpened(self):
#         self.assertEqual(self.sut.chat.toPlainText(),
#                          self.initialGameRoomIdMessage)

#     def test_shouldProperlyDisplayUserMsgInChatAndClearChatEntryLine(self):
#         self.test_shouldDisplayGameRoomIdAfterWindowOpened()

#         message_content = '{}: {}'.format(
#             self.sut.clientContext['username'], 'Hej byczq')
#         cleared_chat_entry = ''
#         self.sut.chatEntryLine.setText(message_content)
#         self.sut.display_user_msg(message_content)

#         self.assertEqual(self.sut.chatEntryLine.text(), cleared_chat_entry
#         self.assertEqual(self.sut.chat.toPlainText(), '{}{}{}'.format(
#             self.initialGameRoomIdMessage, message_content, '\n'))


# if __name__ == '__main__':
#     unittest.main()
