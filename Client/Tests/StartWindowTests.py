import unittest
from unittest.mock import Mock
from unittest.mock import patch
from Application.StartWindow import StartWindow
from Communication.ConnectionHandler import ConnectionHandler
import Communication.SocketMsgHandler
from PyQt5.QtWidgets import QApplication
import sys

# for UT on windows(PowerShell):
# $env:PYTHONPATH = ".\Client\"
#
# python  .\Client\Tests\StartWindowTests.py

app = QApplication(sys.argv)


class TestStartWindow(unittest.TestCase):

    connHandlerMock = Mock(spec=ConnectionHandler)
    clientContextDummy = {}
    clientContextDummy['username'] = ''
    clientContextDummy['roomCode'] = ''

    @classmethod
    def setUp(self):
        self.sut = StartWindow(self.connHandlerMock, self.clientContextDummy)

    @classmethod
    def tearDown(self):
        pass

    def test_shouldValidateNicknameAndFailDueToEmptyValue(self):
        self.assertFalse(self.sut.validate_nickname())

    def test_shouldSuccessfullyValidateNickname(self):
        self.sut.nicknameField.setText('username')
        self.assertTrue(self.sut.validate_nickname())

    def test_shouldValidateRoomCodeAndFailDueToEmptyValue(self):
        self.assertFalse(self.sut.validate_room_code())

    def test_shouldSuccessfullyValidateRoomCode(self):
        self.sut.roomCodeField.setText('abcdefgh')
        self.assertTrue(self.sut.validate_room_code())

    # def test_shouldSuccesfullyPerformWindowCloseEvent(self):
    #     self.connHandlerMock.is_connection_receiver_connected.assert_called_once()
    #     self.sut.closeEvent('event')


if __name__ == '__main__':
    unittest.main()
