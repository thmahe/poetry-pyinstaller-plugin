import logging
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from poetry.core.version.pep440 import PEP440Version
from poetry.factory import Factory

from poetry_pyinstaller_plugin import Target


class TestUtilityFunctions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.patch_platform = patch("poetry_pyinstaller_plugin.utils.get_platform")
        cls.mock_platform = cls.patch_platform.start()
        cls.mock_platform.return_value = "manylinux"

        cls.patch_venv = patch("poetry.utils.env.env_manager.EnvManager.create_venv")
        cls.mock_venv = cls.patch_venv.start()

    @classmethod
    def tearDownClass(cls):
        cls.patch_platform.stop()
        cls.patch_venv.stop()

    def setUp(self):
        self.poetry = Factory().create_poetry(cwd=Path("test_project"))
        self.io = MagicMock()
        self.patch_io_write_line = patch("cleo.io.io.IO.write_line")
        self.mock_write_line = self.patch_io_write_line.start()
        self.io.write_line = self.mock_write_line
        self.target = Target("my-tool-2", self.poetry, self.io)

    def test_init(self):
        Target("my-tool", self.poetry, self.io)
        Target("my-tool-2", self.poetry, self.io)
        Target("my-tool-3", self.poetry, self.io)

    def test__global_config(self):
        self.assertIsNotNone(self.target._global_config)
        self.assertIsNotNone(self.target._global_config.lookup("tool.poetry-pyinstaller-plugin.targets.my-tool"))

    def test__plugin_config(self):
        self.assertEqual(self.target._plugin_config,
                         self.target._global_config.get_section("tool.poetry-pyinstaller-plugin"))

    def test__target_config(self):
        self.assertEqual(self.target._target_config,
                         self.target._global_config.get_section("tool.poetry-pyinstaller-plugin.targets.my-tool-2"))

    def test_prog(self):
        self.assertEqual(self.target.prog, "my-tool-2")

    def test_source(self):
        self.assertEqual(self.target.source, Path("test_project", "test_package", "main.py").resolve())

    def test_platform(self):
        self.assertIsNotNone(self.target.platform)

    def test_package_version(self):
        self.assertEqual(self.target.package_version.to_string(), "0.1.0")
        self.assertFalse(self.target.package_version.is_prerelease())

    def test_work_path(self):
        self.assertEqual(self.target.work_path, Path("test_project", "build", "manylinux").resolve())

    def test_default_type(self):
        self.assertEqual(self.target.type, "onedir")

    def test_default_bundle(self):
        self.assertEqual(self.target.bundle, False)

    def test_default_strip(self):
        self.assertEqual(self.target.strip, False)

    def test_default_no_upx(self):
        self.assertEqual(self.target.no_upx, False)

    def test_default_console(self):
        self.assertEqual(self.target.console, False)

    def test_default_windowed(self):
        self.assertEqual(self.target.windowed, False)

    def test_default_icon(self):
        self.assertEqual(self.target.icon, None)

    def test_default_uac_admin(self):
        self.assertEqual(self.target.uac_admin, False)

    def test_default_uac_uiaccess(self):
        self.assertEqual(self.target.uac_uiaccess, False)

    def test_default_argv_emulation(self):
        self.assertEqual(self.target.argv_emulation, False)

    def test_default_arch(self):
        self.assertEqual(self.target.arch, None)

    def test_default_hidden_import(self):
        self.assertEqual(self.target.hidden_import, None)

    def test_default_when(self):
        self.assertEqual(self.target.when, None)

    def test_default_add_version(self):
        self.assertEqual(self.target.add_version, False)

        self.target = Target("my-tool-3", self.poetry, self.io)
        self.assertEqual(self.target.add_version, True)
        self.assertEqual(self.target.prog, "my-tool-3-0.1.0")

    def test_default_certificates(self):
        self.assertEqual(self.target.certificates, [])

    def test_default_collect_config(self):
        self.assertEqual(self.target.collect_config, dict())

    def test_default_exclude_poetry_include(self):
        self.assertEqual(self.target.exclude_poetry_include, False)

    def test_default_include_config(self):
        self.assertEqual(self.target.include_config, dict())

    def test_default_runtime_hooks(self):
        self.assertEqual(self.target.runtime_hooks, [])

    def test_default_copy_metadata_config(self):
        self.assertEqual(self.target.copy_metadata_config, [])

    def test_default_recursive_copy_metadata_config(self):
        self.assertEqual(self.target.recursive_copy_metadata_config, [])

    def test_default_package_config(self):
        self.assertEqual(self.target.package_config, dict())

    def test_property_pyinstaller_command_simple(self):
        expected = [
            'pyinstaller',
            str(Path("test_project", "test_package", "main.py").resolve()),
            '--onedir',
            '--name', 'my-tool-2',
            '--noconfirm',
            '--clean',
            '--workpath', str(Path("test_project", "build", "manylinux").resolve()),
            '--distpath', str(Path('dist').resolve()),
            '--specpath', str(Path('dist', ".specs").resolve()),
            '--contents-directory', '_my-tool-2_internal',
            '--noconsole',
            '--nowindowed',
            '--add-data', str(Path(os.getcwd()).resolve() / "README.md:."),
            '--log-level=WARN'
        ]
        self.target.dist_path = Path('dist').resolve()
        self.assertEqual(self.target.pyinstaller_command, expected)

    def test_property_pyinstaller_command_full(self):
        expected = [
            'pyinstaller',
            str(Path("test_project", "test_package", "main.py").resolve()),
            '--onefile',
            '--name', 'my-tool-3-0.1.0',
            '--noconfirm',
            '--clean',
            '--workpath', str(Path("test_project", "build", "manylinux").resolve()),
            '--distpath', str(Path("dist").resolve()),
            '--specpath', str(Path("dist", ".specs").resolve()),
            '--contents-directory', '_my-tool-3-0.1.0_internal',
            '--strip',
            '--console',
            '--windowed',
            '--uac-admin',
            '--uac-uiaccess',
            '--argv-emulation',
            '--icon', 'icon.ico',
            '--target-arch', 'amd64',
            '--runtime-hook', 'hooks/my_hook.py',
            '--copy-metadata', 'requests',
            '--recursive-copy-metadata', 'certifi',
            '--collect-submodules', 'package_a',
            '--collect-data', 'package_b',
            '--collect-data', 'package_c',
            '--collect-binaries', 'package_d',
            '--collect-all', 'package_e',
            '--add-data', str(Path(os.getcwd()).resolve() / "file.txt:file.txt"),
            '--hidden-import', 'requests',
            '--hidden-import', 'certifi',
            '--log-level=WARN'
        ]
        self.target = Target("my-tool-3", self.poetry, self.io)
        self.target.dist_path = Path('dist').resolve()
        self.assertEqual(self.target.pyinstaller_command, expected)

    def test__add_collect_args(self):
        expected = [
            '--collect-submodules', 'package_a',
            '--collect-data', 'package_b',
            '--collect-data', 'package_c',
            '--collect-binaries', 'package_d',
            '--collect-all', 'package_e'
        ]
        args = []
        self.target = Target("my-tool-3", self.poetry, self.io)
        self.target._add_collect_args(args)
        self.assertEqual(args, expected)

    def test__add_include_args(self):
        expected = [
            '--add-data', str(Path(os.getcwd()).resolve() / "README.md:."),
        ]
        args = []
        self.target._add_include_args(args)
        self.assertEqual(args, expected)

        expected = [
            '--add-data', str(Path(os.getcwd()).resolve() / "file.txt:file.txt"),
        ]
        args = []
        self.target = Target("my-tool-3", self.poetry, self.io)
        self.target._add_include_args(args)
        self.assertEqual(args, expected)

    def test__add_hidden_imports_args(self):
        args = []
        self.target._add_hidden_imports_args(args)
        self.assertEqual(args, [])

        expected = ['--hidden-import', 'requests']
        args = []
        self.target.hidden_import = "requests"
        self.target._add_hidden_imports_args(args)
        self.assertEqual(args, expected)

        args = []
        self.target.hidden_import = ["requests"]
        self.target._add_hidden_imports_args(args)
        self.assertEqual(args, expected)

    def test__add_logging_args(self):
        args = []
        self.target._add_logging_args(logging.WARNING, args)
        self.assertEqual(args, ['--log-level=WARN'])

        args = []
        self.target._add_logging_args(logging.INFO, args)
        self.assertEqual(args, ['--log-level=INFO'])

        args = []
        self.target._add_logging_args(logging.DEBUG, args)
        self.assertEqual(args, ["--debug=all", "--log-level=DEBUG"])

    def test_validate(self):
        with self.assertRaises(ValueError) as exc:
            self.target.type = "not_a_type"
            self.target.validate()

        self.assertIn(
            "ValueError: Unsupported distribution type for target 'my-tool-2', 'not_a_type' not in ['onefile', 'onedir'].",
            " ".join(exc.exception.args))

        with self.assertRaises(ValueError) as exc:
            self.target.type = "onefile"
            self.target.when = "sunshine"
            self.target.validate()

        self.assertIn(
            "ValueError: Unsupported value for field 'when' for target 'my-tool-2', 'sunshine' not in ['release', 'prerelease'].",
            " ".join(exc.exception.args))

    def test_property_skip(self):
        self.assertFalse(self.target.skip)

        self.target.when = "prerelease"
        self.target.package_version = PEP440Version.parse("1.0.0")
        self.assertTrue(self.target.skip)

        self.target.when = "release"
        self.target.package_version = PEP440Version.parse("1.0.0.a0")
        self.assertTrue(self.target.skip)

        self.target.package_version = PEP440Version.parse("1.0.0.dev0")
        self.assertTrue(self.target.skip)

    def test_build(self):
        command = MagicMock()

        patch_venv = patch("poetry.utils.env.env_manager.EnvManager.create_venv")
        patch_venv = patch("poetry.utils.env.env_manager.EnvManager.create_venv")
        mock_venv = patch_venv.start()

        mock_log = MagicMock()
        self.target.log = mock_log

        self.target.build(self.poetry, command)

        mock_log.assert_any_call('  - Building <c1>my-tool-2</c1>')
        mock_log.assert_any_call('  - Built <success>my-tool-2</success>')

    def test_build_skipped(self):
        command = MagicMock()
        mock_log = MagicMock()
        self.target.log = mock_log
        self.target.when = "prerelease"
        self.assertTrue(self.target.skip)
        self.target.build(self.poetry, command)

        mock_log.assert_called_once_with("<fg=yellow;options=bold> <info>-</info> Skipping my-tool-2 (on prerelease only)</>")

    def test__install_dependencies(self):
        mock_log = MagicMock()
        self.target.log = mock_log
        self.mock_venv.run = MagicMock()
        self.target._install_dependencies(self.mock_venv)

        mock_log.assert_any_call("<debug>run 'poetry install --all-extras --all-groups'</debug>")
        self.mock_venv.run.assert_called()

    def test__deploy_certificates(self):
        mock_log = MagicMock()
        self.target.log = mock_log
        self.target.certificates = ["test.crt", "another.crt"]

        self.mock_venv.run_python_script = MagicMock()
        self.target._deploy_certificates(self.poetry, self.mock_venv)

        mock_log.assert_any_call("  - Adding <c1>test.crt</c1> to certifi")
        mock_log.assert_any_call("  - Adding <c1>another.crt</c1> to certifi")
        self.mock_venv.run_python_script.assert_called()

    def test__run_pyinstaller(self):
        mock_log = MagicMock()
        self.target.log = mock_log
        self.mock_venv.run = MagicMock()
        self.target.dist_path = Path("dist")
        self.target._run_pyinstaller(self.mock_venv)
        self.mock_venv.run.assert_called()
