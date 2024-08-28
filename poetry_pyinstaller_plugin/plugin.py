# MIT License
#
# Copyright (c) 2024 Thomas Mahé <contact@tmahe.dev>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = "Thomas Mahé <contact@tmahe.dev>"

import enum
import logging
import os
import sys
import textwrap
from importlib import reload
from pathlib import Path
from typing import List, Dict, Optional, Union
from shutil import copytree, copy
from errno import ENOTDIR, EINVAL, EEXIST
from importlib.machinery import SourceFileLoader

# Reload logging after PyInstaller import (conflicts with poetry logging)
reload(logging)

from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND, TERMINATE
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO

from poetry.poetry import Poetry
from poetry.utils.env import VirtualEnv, ephemeral_environment
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand
from poetry.core.masonry.builders.wheel import WheelBuilder
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_pyinstaller_plugin import add_folder_to_wheel_data_script

def _glob(root_dir: str, end_with: str):
    file_list = []
    for root, directories, files in os.walk(root_dir):
        for file in files:
            if file.endswith(end_with):
                file_list.append(file)
    return file_list

class PyinstDistType(enum.Enum):
    DIRECTORY = "onedir"
    SINGLE_FILE = "onefile"

    @classmethod
    def list(cls):
        return [d.value for d in cls]

    @property
    def pyinst_flags(self):
        return f"--{self.value}"


class PyInstallerTarget(object):
    _platform: str

    def __init__(self,
        prog: str,
        source: str,
        type: str = "onedir",
        bundle: bool = False,
        strip: bool = False,
        noupx: bool = False,
        console: bool = False,
        windowed: bool = False,
        icon: Optional[str] = None,
        uac_admin: bool = False,
        uac_uiaccess: bool = False,
        argv_emulation: bool = False,
        arch: Optional[str] = None,
        hiddenimport: Optional[Union[str, List[str]]] = None,
        runtime_hooks: Optional[List[str]] = None,
    ):
        self.prog = prog
        self.source = Path(source).resolve()
        self.type = self._validate_type(type)

        self.bundled = bundle
        self.strip = strip
        self.noupx = noupx
        self.console = console
        self.windowed = windowed
        self.icon = Path(icon).resolve() if icon else None
        self.uac_admin = uac_admin
        self.uac_uiaccess = uac_uiaccess
        self.argv_emulation = argv_emulation
        self.arch = arch
        self.hiddenimport = hiddenimport
        self.runtime_hooks = runtime_hooks

    def _validate_type(self, type: str):
        if type not in PyinstDistType.list():
            raise ValueError(
                f"ValueError: Unsupported distribution type for target '{self.prog}', "
                f"'{type}' not in {PyinstDistType.list()}."
            )
        return PyinstDistType(type)

    def build(self,
              io,
              venv: VirtualEnv,
              platform: str,
              collect_config: Dict,
              copy_metadata: List,
              recursive_copy_metadata: List,
              poetry_include_config: List,
              include_config: Dict,
              package_config: Dict
              ):
        self._platform = platform
        work_path = Path("build", platform)
        dist_path = Path("dist", "pyinstaller", platform)

        args = [
            str(self.source),
            self.type.pyinst_flags,
            "--name", self.prog,
            "--noconfirm",
            "--clean",
            "--workpath", str(work_path),
            "--distpath", str(dist_path),
            "--specpath", str(dist_path / ".specs"),
            "--paths", str(venv.site_packages.path),
            "--log-level=WARN",
            "--contents-directory", f"_{self.prog}_internal"
        ]

        collect_args = []
        for collect_type, modules in collect_config.items():
            if collect_type in ["submodules", "data", "datas", "binaries", "all"]:
                for module in modules:
                    collect_args.append(f"--collect-{collect_type}")
                    collect_args.append(module)

        args += collect_args

        if include_config or poetry_include_config:
            include_args = []
            sep = ";" if "win" in platform else ":"

            for source, target in include_config.items():
                if source and target:
                    include_args.append("--add-data")
                    include_args.append(f"{Path(source).resolve()}{sep}{target}")

            for item in poetry_include_config:
                path = item if isinstance(item, str) else item.get("path")
                if path:
                    include_args.append("--add-data")
                    include_args.append(f"{Path(path).resolve()}{sep}.")

            args += include_args

        if self.strip:
            args.append("--strip")
        if self.noupx:
            args.append("--noupx")
        if self.console:
            args.append("--console")
        if self.windowed:
            args.append("--windowed")
        if self.icon:
            args.append("--icon")
            args.append(self.icon)
        if self.uac_admin:
            args.append("--uac-admin")
        if self.uac_uiaccess:
            args.append("--uac-uiaccess")
        if self.argv_emulation:
            args.append("--argv-emulation")
        if self.arch:
            args.append("--target-arch")
            args.append(self.arch)
        if self.hiddenimport:
            if isinstance(self.hiddenimport, str):
                self.hiddenimport = [self.hiddenimport]
            for h in self.hiddenimport:
                args.append("--hidden-import")
                args.append(h)

        if self.runtime_hooks:
            for hook in self.runtime_hooks:
                args.append("--runtime-hook")
                args.append(hook)

        for package in copy_metadata:
            args.append("--copy-metadata")
            args.append(package)

        for package in recursive_copy_metadata:
            args.append("--recursive-copy-metadata")
            args.append(package)

        if logging.root.level == logging.WARNING:
            args.append(f"--log-level=WARN")
        if logging.root.level == logging.INFO:
            args.append(f"--log-level=INFO")
        if logging.root.level == logging.DEBUG:
            args.append("--debug=all")
            args.append(f"--log-level=DEBUG")

        pyinst_build = venv.run(str(Path(venv.script_dirs[0]) / "pyinstaller"), *args)
        output = textwrap.indent(pyinst_build, " " * 6)
        io.write(f"<debug>{output}</debug>")

        if package_config:
            package_path = Path("dist", "pyinstaller", platform, self.prog)
            for source, target in package_config.items():
                destination = Path(package_path / (target if target != "." else source))
                try:
                    copytree(source, destination)
                except OSError as exc: # python >2.5 or, is file and/or file exists
                    if exc.errno in (ENOTDIR, EINVAL, EEXIST):
                        copy(source, destination)
                    else:
                        raise

    def bundle_wheel(self, io):
        wheels = glob.glob("*-py3-none-any.whl", root_dir="dist")
        for wheel in wheels:
            if self._platform and self.prog:
                folder_to_add = Path("dist", "pyinstaller", self._platform, self.prog)

                io.write_line(f"  - Adding <c1>{self.prog}</c1> to data scripts <debug>{wheel}</debug>")

                add_folder_to_wheel_data_script(folder_to_add, Path("dist", wheel))

class PyInstallerPluginHook(object):
    """
    Generic interface for interacting with Poetry in hooks
    """

    def __init__(
        self, io: IO, venv: VirtualEnv, poetry: Poetry, platform: str
    ) -> None:
        self._io = io
        self._venv = venv
        self.poetry = poetry
        self.platform = platform

    @property
    def pyproject_data(self) -> Dict:
        """
        Get pyproject data
        :return: Configuration file dictionary
        """
        return self.poetry.pyproject.data

    def run(self, command: str, *args: str) -> None:
        """
        Run command in virtual environment
        """
        self._venv.run(command, *args)

    def run_pip(self, *args: str) -> None:
        """
        Install requirements in virtual environment
        """
        return self._venv.run_pip(*args)

    def write_line(self, output: str) -> None:
        """
        Output message
        """
        self._io.write_line(output)

class PyInstallerPlugin(ApplicationPlugin):
    _app: Application = None

    _targets: List[PyInstallerTarget]

    def __init__(self):
        self._targets = []

    @property
    def version_opt(self) -> Dict:
        """
        Get pyinstaller version option
        :return: Version string of pyinstaller plugin
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("version", None)
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def scripts_opt_block(self) -> Dict:
        """
        Get plugins scripts options block
        :return: Dictionary of { "program": Path | Dictionary }
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("scripts", {})
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def certifi_opt_block(self) -> Dict:
        """
        Get certifi config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("certifi", {})
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def collect_opt_block(self) -> Dict:
        """
        Get collect config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("collect", {})
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def poetry_include_opt_block(self) -> List:
        """
        Get poetry include config
        """
        data = self._app.poetry.pyproject.data
        if data:
            if not data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("exclude-include", False):
                return data.get("tool", {}).get("poetry", {}).get("include", [])
            return []
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def use_poetry_install(self) -> bool:
        """
        Get status of option "use-poetry-install"
        """
        data = self._app.poetry.pyproject.data

        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("use-poetry-install", False)
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def include_opt_block(self) -> Dict:
        """
        Get pyinstaller include config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("include", {})
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def package_opt_block(self) -> Dict:
        """
        Get package config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("package", {})
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def copy_metadata_opt_block(self) -> List:
        """
        Get copy-metadata config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("copy-metadata", [])
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def recursive_copy_metadata_opt_block(self) -> List:
        """
        Get recursive-copy-metadata config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("recursive-copy-metadata", [])
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def pre_build_opt_block(self) -> str:
        """
        Get pre-build hook config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("pre-build", None)
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def post_build_opt_block(self) -> str:
        """
        Get post-build hook config
        """
        data = self._app.poetry.pyproject.data
        if data:
            return data.get("tool", {}).get("poetry-pyinstaller-plugin", {}).get("post-build", None)
        raise RuntimeError("Error while retrieving pyproject.toml data.")

    @property
    def _use_bundle(self):
        return True in [t.bundled for t in self._targets]

    def activate(self, application: Application) -> None:
        """
        Activation method for ApplicationPlugin
        """
        self._app = application

        application.event_dispatcher.add_listener(COMMAND, self._build_binaries)
        application.event_dispatcher.add_listener(TERMINATE, self._bundle_wheels)

    def _parse_targets(self) -> List[PyInstallerTarget]:
        """
        Parse PyInstallerTarget from pyproject.toml
        :return: List of PyInstallerTarget objects
        """
        targets = []
        for prog_name, content in self.scripts_opt_block.items():
            # Simplest binding: prog_name = "package.source"
            if isinstance(content, str):
                targets.append(PyInstallerTarget(prog=prog_name, source=content))
            elif isinstance(content, dict):
                targets.append(PyInstallerTarget(prog=prog_name, **content))
        return targets

    def _update_wheel_platform_tag(self, io: IO) -> None:
        """
        Update platform tag to make wheel platform specific.
        Required for wheels with bundled binaries if no custom build-script is provided to poetry.

        :param io: Used for logging
        :return: None
        """

        platform = WheelBuilder(self._app.poetry)._get_sys_tags()[0].split("-")[-1]

        wheels = _glob(root_dir="dist", end_with="*-py3-none-any.whl")
        if len(wheels) > 0:
            io.write_line(f"Replacing <info>platform</info> in wheels <b>({platform})</b>")
            for wheel in wheels:
                new = wheel.replace("-any.whl", f"-{platform}.whl")
                os.replace(Path("dist", wheel), Path("dist", new))
                io.write_line(f"  - {new}")

    def _load_hook_module(self, module_path: str):
        _module = module_path.split(".")[-1]
        full_module_path = (self._app.poetry.pyproject_path.parent / Path(*module_path.split(".")[:-1]) / f"{_module}.py")
        return SourceFileLoader(_module, str(full_module_path)).load_module()


    def _build_binaries(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher) -> None:
        """
        Build binaries for every target with PyInstaller. Performed before wheel packaging.
        """
        command = event.command

        if not isinstance(command, BuildCommand):
            return

        io = event.io

        self._targets = self._parse_targets()
        if len(self._targets) > 0:

            use_bundle = True in [t.bundled for t in self._targets]
            fmt = io.input.option("format")

            if fmt == "wheel" and not use_bundle:
                return # Skip Pyinstaller build if --format=wheel and no bundled binaries
            if fmt == "sdist":
                return # Skip Pyinstaller build if --format=sdist

            extra_indexes = {s.name: s.url for s in self._app.poetry.get_sources()}
            platform = WheelBuilder(self._app.poetry)._get_sys_tags()[0].split("-")[-1]

            if command.env.is_venv():
                venv = command.env
            else:
                venv = ephemeral_environment(executable=command.env.python if command.env else None)

            if getattr(venv, "path", None) is None:
                io.write_line("<fg=black;bg=yellow>Skipping PyInstaller build, requires virtualenv.</>")
                return

            pip_args = []

            pyinstaller_package = "pyinstaller" if self.version_opt is None else f"pyinstaller=={self.version_opt}"
            pip_args.append(pyinstaller_package)

            pip_args.extend(("certifi", "cffi"))

            for requirement in self._app.poetry.package.requires:
                pip_r = requirement.base_pep_508_name_resolved.replace(' (', '').replace(')', '')

                extra_index_url = []
                if requirement.source_name:
                    extra_index_url = ["--extra-index-url", extra_indexes[requirement.source_name]]

                if requirement.marker.validate({"sys_platform": sys.platform}):
                    io.write_line(f"  - Installing <c1>{requirement}</c1>" +
                                  (
                                      f" <debug>[{requirement.source_name}]</debug>" if requirement.source_name else ""))

                pip_args.extend(extra_index_url)
                pip_args.append(pip_r)

            if not self.use_poetry_install:
                venv_pip = venv.run_pip(
                    "install",
                    "--disable-pip-version-check",
                    "--ignore-installed",
                    "--no-input",
                    *pip_args,
                )
                if event.io.is_debug():
                    io.write_line(f"<debug>{venv_pip}</debug>")

            pyinstaller_version = venv.run("pyinstaller", "--version").strip()
            io.write_line(
                f"<b>Preparing</b> PyInstaller <b><c1>{pyinstaller_version}</b></c1> environment <debug>{venv.path}</debug>")

            for cert in self.certifi_opt_block.get('append', []):
                cert_path = (self._app.poetry.pyproject_path.parent / cert).relative_to(
                    self._app.poetry.pyproject_path.parent)

                io.write_line(f"  - Adding <c1>{cert_path}</c1> to certifi")
                venv.run_python_script(textwrap.dedent(f"""
                import certifi
                print(certifi.where())
                with open(r"{cert_path}", "r") as include:
                    with open(certifi.where(), 'a') as cert:
                        cert.write(include.read())
                """))

            if self.pre_build_opt_block:
                _module_path, _callable = self.pre_build_opt_block.split(":")
                module = self._load_hook_module(_module_path)
                if hasattr(module, _callable):
                    io.write_line(
                        f"<b>Running</b> pre-build hook <debug>{module.__name__}.{_callable}()</debug>")
                    getattr(module, _callable)(
                        PyInstallerPluginHook(io, venv, self._app.poetry, platform)
                    )
                else:
                    io.write_line(f"<fg=black;bg=yellow>Skipping pre-build hook, method {_callable} not found in {module.__name__}.</>")

            io.write_line(
                f"Building <c1>binaries</c1> with PyInstaller <c1>Python {venv.version_info[0]}.{venv.version_info[1]}</c1> <debug>[{platform}]</debug>")
            for t in self._targets:
                io.write_line(f"  - Building <info>{t.prog}</info> <debug>{t.type.name}{' BUNDLED' if t.bundled else ''}{' NOUPX' if t.noupx else ''}</debug>")
                t.build(io=io, venv=venv, platform=platform,
                        collect_config=self.collect_opt_block,
                        copy_metadata=self.copy_metadata_opt_block,
                        recursive_copy_metadata=self.recursive_copy_metadata_opt_block,
                        poetry_include_config=self.poetry_include_opt_block,
                        include_config=self.include_opt_block,
                        package_config=self.package_opt_block,
                        )
                io.write_line(f"  - Built <success>{t.prog}</success> -> <success>'{Path('dist', 'pyinstaller', platform, t.prog)}'</success>")

            if self.post_build_opt_block:
                _module_path, _callable = self.post_build_opt_block.split(":")
                module = self._load_hook_module(_module_path)
                if hasattr(module, _callable):
                    io.write_line(
                        f"<b>Running</b> post-build hook <debug>{module.__name__}.{_callable}()</debug>")
                    getattr(module, _callable)(
                        PyInstallerPluginHook(io, venv, self._app.poetry, platform)
                    )
                else:
                    io.write_line(f"<fg=black;bg=yellow>Skipping post-build hook, method {_callable} not found in {module.__name__}.</>")

            if fmt == "pyinstaller":
                sys.exit(0)

    def _bundle_wheels(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher) -> None:
        """
        Include binaries in wheels under data/scripts. Performed on completion of `poetry build` command.
        """
        command = event.command
        if not isinstance(command, BuildCommand):
            return

        io = event.io
        if self._use_bundle:
            for t in self._targets:
                if t.bundled:
                    t.bundle_wheel(io)

            self._update_wheel_platform_tag(io)
