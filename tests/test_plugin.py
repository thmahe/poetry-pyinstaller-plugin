from unittest import TestCase
from unittest.mock import MagicMock

from poetry.console.application import Application

from poetry_pyinstaller_plugin import __version__
from poetry_pyinstaller_plugin.plugin import (PyInstallerBuildCommand,
                                              PyInstallerShowCommand)


class TestPyInstallerShowCommand(TestCase):

    def test_handle(self):
        io = MagicMock()
        io.is_debug = MagicMock(return_value=False)
        command = PyInstallerShowCommand()
        command._io = io
        return_code = command.handle()
        self.assertEqual(return_code, 0)
        io.write_line.assert_called_with(f'poetry-pyinstaller-plugin {__version__}')


class TestPyInstallerBuildCommand(TestCase):

    def test_handle_no_build(self):
        io = MagicMock()
        io.is_debug = MagicMock(return_value=False)
        app = Application()
        command = PyInstallerBuildCommand(app)
        command._io = io
        return_code = command.handle()
        self.assertEqual(return_code, 0)
        io.write_line.assert_called_with(f'<fg=yellow;options=bold>No targets definition found, nothing to build with pyinstaller.</>')
