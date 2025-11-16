import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from poetry.core.factory import Factory
from poetry.poetry import Poetry
from tomlkit import TOMLDocument, parse

from poetry_pyinstaller_plugin.utils import (LoggingMixin, PyProjectConfig,
                                             get_base_modules_path,
                                             get_output_path, get_platform)


class TestLoggingMixin(TestCase):

    def enable_debug(self):
        self.io.is_debug.return_value = True

    def disable_debug(self):
        self.io.is_debug.return_value = False

    def setUp(self):
        self.io = MagicMock()
        self.patch_io_write_line = patch("cleo.io.io.IO.write_line")
        self.mock_write_line = self.patch_io_write_line.start()
        self.io.write_line = self.mock_write_line

        self.logger = LoggingMixin(self.io)
        self.assertEqual(self.logger._io, self.io)
        self.disable_debug()

    def tearDown(self):
        self.disable_debug()
        self.mock_write_line.stop()

    def test_is_debug(self):
        self.assertFalse(self.logger.is_debug())

        self.enable_debug()
        self.assertTrue(self.logger.is_debug())

    def test_attach_io(self):
        self.assertEqual(self.logger._io, self.io)
        self.logger.attach_io("Custom IO")
        self.assertEqual(self.logger._io, "Custom IO")

    def test_log(self):
        self.logger.log("msg")
        self.mock_write_line.assert_called_with("msg")

        self.enable_debug()
        self.logger.log("msg")
        self.mock_write_line.assert_called_with("<fg=yellow;options=bold>[poetry-pyinstaller-plugin]</> msg")

    def test_warning(self):
        self.logger.warning("msg")
        self.mock_write_line.assert_called_with("<fg=yellow;options=bold>msg</>")

    def test_error(self):
        self.logger.error("msg")
        self.mock_write_line.assert_called_with("<error>msg</error>")

    def test_debug(self):
        self.logger.debug("msg")
        self.mock_write_line.assert_not_called()

        self.enable_debug()
        self.logger.debug("msg")
        self.mock_write_line.assert_called_with(
            "<fg=yellow;options=bold>[poetry-pyinstaller-plugin]</> <debug>msg</debug>")

    def test_command(self):
        self.logger.debug_command(f"line1{os.linesep}line2")
        self.mock_write_line.assert_not_called()

        self.enable_debug()
        self.logger.debug_command(f"line1{os.linesep}line2")
        self.mock_write_line.assert_any_call(
            "<fg=yellow;options=bold>[poetry-pyinstaller-plugin]</> <debug> + line1</debug>")
        self.mock_write_line.assert_any_call(
            "<fg=yellow;options=bold>[poetry-pyinstaller-plugin]</> <debug> + line2</debug>")


class TestUtilityFunctions(TestCase):

    def test_get_platform(self):
        poetry = Factory().create_poetry(cwd=Path("test_project"))
        patch_wheel_builder = patch("poetry.core.masonry.builders.wheel.WheelBuilder._get_sys_tags")
        mock_wheel_sys_tags = patch_wheel_builder.start()
        mock_wheel_sys_tags.return_value = ['cp312-cp312-manylinux_2_39_x86_64', 'cp312-cp312-manylinuxxx_2_38_x86_64']

        self.assertEqual(get_platform(poetry), "manylinux_2_39_x86_64")

    def test_get_base_modules_path(self):
        poetry = Factory().create_poetry(cwd=Path("test_project"))
        self.assertEqual(get_base_modules_path(poetry), [Path("test_project")])

    def test_get_output_path(self):
        command = MagicMock()

        command.option.return_value = None
        self.assertEqual(get_output_path(command), Path("dist").resolve())

        command.option.return_value = "custom"
        self.assertEqual(get_output_path(command), Path("custom").resolve())


class TestPyProjectConfig(TestCase):

    @classmethod
    def setUpClass(cls):
        toml_str = """
        root_key = "test"
        [tool.poetry-pyinstaller-plugin]
        pre-build = "hooks.pyinstaller:pre_build"
        post-build = "hooks.pyinstaller:post_build"
        
        [tool.poetry-pyinstaller-plugin.targets.my-tool]
        source = "test_package/main.py"
        bundle = true
        """

        doc = parse(toml_str)
        cls.config = PyProjectConfig(doc)

    def test_lookup(self):
        self.assertEqual(self.config.lookup("root_key"), "test")
        self.assertEqual(self.config.lookup("does_not_exist", "default_value"), "default_value")
        self.assertEqual(self.config.lookup("tool.poetry-pyinstaller-plugin.pre-build"), "hooks.pyinstaller:pre_build")

    def test_lookup_exception(self):
        with self.assertRaises(RuntimeError) as exc:
            PyProjectConfig(None).lookup("does_not_exist")

        self.assertEqual(exc.exception.args, ('Error while retrieving pyproject.toml data.',))

    def test_get_section(self):
        sub_section = self.config.get_section("tool.poetry-pyinstaller-plugin.targets.my-tool")
        self.assertEqual(sub_section.lookup("source"), "test_package/main.py")
