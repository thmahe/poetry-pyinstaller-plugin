import os
import textwrap
from pathlib import Path
from typing import Callable
from unittest import TestCase
from unittest.mock import MagicMock, patch

from poetry_pyinstaller_plugin import PluginHook
from poetry_pyinstaller_plugin.hooks import PostHook, PreHook


class TestPluginHook(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.patch_platform = patch("poetry_pyinstaller_plugin.utils.get_platform")
        cls.patch_base_module_path = patch("poetry_pyinstaller_plugin.utils.get_base_modules_path")
        cls.mock_platform = cls.patch_platform.start()
        cls.mock_base_module_path = cls.patch_base_module_path.start()
        cls.mock_platform.return_value = "linux"
        cls.mock_base_module_path.return_value = [Path("test_project")]

    @classmethod
    def tearDownClass(cls):
        cls.patch_platform.stop()
        cls.mock_base_module_path.stop()

    def setUp(self):
        self.hook = PluginHook(application=MagicMock(),
                               module_name="test_package.main",
                               callable_name="hello_world")
        self.hook.type = "test"

    def test_name(self):
        self.assertEqual(self.hook.name, "test_package.main:hello_world")

    def test_platform(self):
        self.assertEqual(self.hook.platform, "linux")

    def test_callable(self):
        self.assertEqual(self.hook._hook.__name__, "hello_world")
        self.assertEqual(self.hook._hook(None), "hello world")

    def test__get_source_path(self):
        self.assertEqual(self.hook._get_source_path("test_package.main"), Path("test_project", "test_package", "main.py"))

    def test__get_source_path_exception(self):
        with self.assertRaises(RuntimeError) as exc:
            self.hook._get_source_path("test_package.main_does_not_exist")

        self.assertEqual(exc.exception.args,
                         ("Unable to find module 'test_package.main_does_not_exist' in current project.",))

    def test__get_callable(self):
        self.assertIsInstance(self.hook._get_callable("test_package.main", "hello_world"), Callable)

    def test__get_callable_not_found(self):
        self.assertIsNone(self.hook._get_callable("test_package.main", "does_not_exist"))

    def test__exec(self):
        venv = MagicMock()
        self.hook.log = MagicMock()

        self.hook._exec(venv)
        msg = f"<info>Running<info> {self.hook.type}-build hook <debug>'test_package.main:hello_world'</debug>"
        self.hook.log.assert_called_with(msg)

    def test__exec_no_callable(self):
        venv = MagicMock()
        self.hook.warning = MagicMock()

        self.hook._hook = None
        self.hook._exec(venv)
        msg = f"Skipping {self.hook.type}-build hook, 'hello_world' callable not found in test_package.main."
        self.hook.warning.assert_called_with(msg)

    def test_run(self):
        self.hook.debug = MagicMock()
        self.hook._venv = MagicMock()
        self.hook._venv.run = MagicMock(return_value=f"hello world !{os.linesep}")

        self.hook.run("echo", "hello world !")

        self.hook._venv.run.assert_called_with("echo", "hello world !")

        self.hook.debug.assert_any_call("Running 'echo hello world !'")
        self.hook.debug.assert_any_call("++ hello world !")
        self.hook.debug.assert_any_call("++ ")

    def test_run_pip(self):
        self.hook.debug = MagicMock()
        self.hook._venv = MagicMock()

        pip_stdout = textwrap.dedent("""\
        Collecting termkit
            Downloading termkit-0.2.13-py3-none-any.whl.metadata (2.5 kB)
        Downloading termkit-0.2.13-py3-none-any.whl (10 kB)
        Installing collected packages: termkit
        
        [notice] A new release of pip is available: 23.2.1 -> 25.3
        [notice] To update, run: pip install --upgrade pip
        """).replace("\n", os.linesep)

        self.hook._venv.run_pip = MagicMock(return_value=pip_stdout)

        self.hook.run_pip("install", "termkit")

        self.hook._venv.run_pip.assert_called_with("install", "termkit")

        assert_debug = self.hook.debug.assert_any_call

        assert_debug("Running 'pip install termkit'")
        assert_debug("++ Collecting termkit")
        assert_debug("++     Downloading termkit-0.2.13-py3-none-any.whl.metadata (2.5 kB)")
        assert_debug("++ Downloading termkit-0.2.13-py3-none-any.whl (10 kB)")
        assert_debug("++ Installing collected packages: termkit")
        assert_debug("++ ")
        assert_debug("++ [notice] A new release of pip is available: 23.2.1 -> 25.3")
        assert_debug("++ [notice] To update, run: pip install --upgrade pip")
        assert_debug("++ ")


class TestPreHook(TestPluginHook):

    def setUp(self):
        self.hook = PreHook(application=MagicMock(),
                            module_name="test_package.main",
                            callable_name="hello_world")

    def test_type(self):
        self.assertEqual(self.hook.type, "pre")


class TestPostHook(TestPluginHook):

    def setUp(self):
        self.hook = PostHook(application=MagicMock(),
                             module_name="test_package.main",
                             callable_name="hello_world")

    def test_type(self):
        self.assertEqual(self.hook.type, "post")
