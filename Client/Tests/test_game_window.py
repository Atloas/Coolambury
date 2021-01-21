import pytest
from Application.GameWindow import GameWindow
from Communication.ConnectionHandler import ConnectionHandler

# TODO: Replace unittest.mock with PyTestMock
from unittest.mock import Mock
import pytest


# for UT on windows(PowerShell):
# $env:PYTHONPATH = ".\Client\"
#
# pytest .\Client\Tests\
@pytest.fixture
def gameWindowFixutre(qtbot):
    connHandlerMock = Mock(spec=ConnectionHandler)
    client_context_dummy = {}
    client_context_dummy['username'] = 'test_user'
    client_context_dummy['roomCode'] = 'abcdefgh'
    sut = GameWindow(client_context_dummy, connHandlerMock)
    qtbot.addWidget(sut)

    pytest.initial_game_room_id_message = 'GAME ROOM ID: {}'.format(
        client_context_dummy['roomCode']
    )
    pytest.cleared_chat_entry = ''
    return sut


def _assert_that_chat_contains_message(message_content: dict, gameWindowFixutre):
    message_text = '{}: {}'.format(message_content['author'], message_content['message'])

    actual_chat_contents_after_first_chat_msg = '{}\n{}'.format(
        pytest.initial_game_room_id_message, message_text
    )

    assert gameWindowFixutre.chat.toPlainText() == actual_chat_contents_after_first_chat_msg


def _assert_that_chat_contains_text(message_content: str, gameWindowFixutre):
    actual_chat_contents_after_first_chat_msg = '{}\n{}'.format(
        pytest.initial_game_room_id_message, message_content
    )

    assert gameWindowFixutre.chat.toPlainText() == actual_chat_contents_after_first_chat_msg


def test_should_display_game_room_id_after_window_opened(gameWindowFixutre):
    assert gameWindowFixutre.chat.toPlainText() == pytest.initial_game_room_id_message


def test_should_properly_display_user_msg_in_chat_and_clear_chat_entry_line(gameWindowFixutre):
    test_should_display_game_room_id_after_window_opened(gameWindowFixutre)

    # fmt: off
    message_content = {
        'author': gameWindowFixutre.client_context['username'],
        'message': 'Hello Everybody'
    }
    # fmt: on

    message_text = '{}: {}'.format(message_content['author'], message_content['message'])

    gameWindowFixutre.chat_entry_line.setText(message_text)
    gameWindowFixutre.display_message(message_content)

    assert gameWindowFixutre.chat_entry_line.text() == pytest.cleared_chat_entry

    _assert_that_chat_contains_message(message_content, gameWindowFixutre)


def test_should_properly_display_server_announcement_message(gameWindowFixutre):
    # fmt: off
    message_from_server = {
        'author': 'SERVER',
        'message': 'A VERY IMPORTANT ANNOUNCEMENT FROM THE SERVER',
    }
    # fmt: on
    gameWindowFixutre.display_message(message_from_server)

    assert gameWindowFixutre.chat_entry_line.text() == pytest.cleared_chat_entry

    actual_chat_contents_after_first_chat_msg = '{}\n{}'.format(
        pytest.initial_game_room_id_message, message_from_server
    )


def test_chat_entry_line_clears_after_adding_message_to_chat(gameWindowFixutre):
    # fmt: off
    chat_entry = {
        'author': gameWindowFixutre.client_context['username'],
        'message': 'Cat!'
    }
    # fmt: on
    gameWindowFixutre.chat_entry_line.setText(chat_entry['message'])
    gameWindowFixutre.display_user_message(chat_entry)

    assert gameWindowFixutre.chat_entry_line.text() == ''

    _assert_that_chat_contains_message(chat_entry, gameWindowFixutre)


def test_game_start_displays_proper_chat_message(gameWindowFixutre):
    game_start_message = 'Game started!'
    gameWindowFixutre.display_system_message(game_start_message)
    _assert_that_chat_contains_text(game_start_message, gameWindowFixutre)
