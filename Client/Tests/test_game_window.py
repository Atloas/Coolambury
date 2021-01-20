import pytest

# TODO: Replace unittest.mock with PyTestMock
from unittest.mock import Mock
from Application.GameWindow import GameWindow
from Communication.ConnectionHandler import ConnectionHandler


# for UT on windows(PowerShell):
# $env:PYTHONPATH = '.\Client\'
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

    pytest.initialGameRoomIdMessage = 'GAME ROOM ID: {}'.format(clientContextDummy['roomCode'])
    pytest.cleared_chat_entry = ''
    return sut


def _assert_that_chat_contains_message(message_content: dict, gameWindowFixutre):
    message_text = '{}: {}'.format(message_content['author'], message_content['message'])

    actual_chat_contents_after_first_chat_msg = '{}\n{}'.format(pytest.initialGameRoomIdMessage, message_text)

    assert gameWindowFixutre.chat.toPlainText() == actual_chat_contents_after_first_chat_msg


def _assert_that_chat_contains_text(message_content: str, gameWindowFixutre):
    actual_chat_contents_after_first_chat_msg = '{}\n{}'.format(pytest.initialGameRoomIdMessage, message_content)

    assert gameWindowFixutre.chat.toPlainText() == actual_chat_contents_after_first_chat_msg


def test_should_display_game_room_id_after_window_opened(gameWindowFixutre):
    assert gameWindowFixutre.chat.toPlainText() == pytest.initialGameRoomIdMessage


def test_should_properly_display_user_msg_in_chat_and_clear_chat_entry_line(gameWindowFixutre):
    test_should_display_game_room_id_after_window_opened(gameWindowFixutre)
    pytest.initialGameRoomIdMessage = 'GAME ROOM ID: {}'.format(gameWindowFixutre.clientContext['roomCode'])

    message_content = {'author': gameWindowFixutre.clientContext['username'], 'message': 'Hello Everybody'}
    message_text = '{}: {}'.format(message_content['author'], message_content['message'])

    gameWindowFixutre.chatEntryLine.setText(message_text)
    gameWindowFixutre.display_message(message_content)

    assert gameWindowFixutre.chatEntryLine.text() == pytest.cleared_chat_entry

    _assert_that_chat_contains_message(message_content, gameWindowFixutre)


def test_should_properly_display_server_announcement_message(gameWindowFixutre):
    message_from_server = {'author': 'SERVER', 'message': 'A VERY IMPORTANT ANNOUNCEMENT FROM THE SERVER'}
    gameWindowFixutre.display_message(message_from_server)

    assert gameWindowFixutre.chatEntryLine.text() == pytest.cleared_chat_entry

    actual_chat_contents_after_first_chat_msg = '{}\n{}'.format(pytest.initialGameRoomIdMessage, message_from_server)


def test_chat_entry_line_clears_after_adding_message_to_chat(gameWindowFixutre):
    chat_entry = {'author': gameWindowFixutre.clientContext['username'], 'message': 'Cat!'}
    gameWindowFixutre.chatEntryLine.setText(chat_entry['message'])
    gameWindowFixutre.display_user_message(chat_entry)

    assert gameWindowFixutre.chatEntryLine.text() == ''

    _assert_that_chat_contains_message(chat_entry, gameWindowFixutre)


def test_game_start_displays_proper_chat_message(gameWindowFixutre):
    game_start_message = 'Game started!'
    gameWindowFixutre.display_system_message(game_start_message)
    _assert_that_chat_contains_text(game_start_message, gameWindowFixutre)
