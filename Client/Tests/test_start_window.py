import pytest
# TODO: Replace unittest.mock with PyTestMock
from unittest.mock import Mock
from Application.StartWindow import StartWindow
from Communication.ConnectionHandler import ConnectionHandler

# for UT on windows(PowerShell):
# $env:PYTHONPATH = ".\Client\"
#
# pytest .\Client\Tests\


@pytest.fixture
def startWindowFixutre(qtbot):
    connHandlerMock = Mock(spec=ConnectionHandler)
    clientContextDummy = {}
    clientContextDummy['username'] = ''
    clientContextDummy['roomCode'] = ''
    sut = StartWindow(connHandlerMock, clientContextDummy)
    qtbot.addWidget(sut)
    return sut


def test_should_validate_nickname_and_fail_due_to_empty_value(startWindowFixutre, qtbot):
    assert startWindowFixutre.validate_nickname() == False


def test_should_successfully_validate_nickname(startWindowFixutre, qtbot):
    startWindowFixutre.nicknameField.setText('username')
    assert startWindowFixutre.validate_nickname() == True


def test_should_validate_room_code_and_fail_due_to_empty_value(startWindowFixutre, qtbot):
    assert startWindowFixutre.validate_room_code() == False


def test_should_validate_room_code_and_fail_due_to_code_too_short(startWindowFixutre, qtbot):
    startWindowFixutre.roomCodeField.setText('abcde')
    assert startWindowFixutre.validate_room_code() == False


def test_should_successfully_validate_room_code(startWindowFixutre, qtbot):
    startWindowFixutre.roomCodeField.setText('abcdefgh')
    assert startWindowFixutre.validate_room_code() == True
