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
import glob
import logging
import os
import sys
from importlib import reload
from pathlib import Path
from typing import List, Dict

import PyInstaller.__main__

# Reload logging after PyInstaller import (conflicts with poetry logging)
reload(logging)

from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND, TERMINATE
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand
from poetry.core.masonry.builders.wheel import WheelBuilder
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_pyinstaller_plugin import add_folder_to_wheel_data_script


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
    def __init__(self, prog: str, source: str, type: str = "onedir", bundle: bool = False):
        self.prog = prog
        self.source = Path(source).resolve()
        self.type = self._validate_type(type)
        self.bundled = bundle

    @property
    def _site_packages(self):
        if sys.platform == "win32":
            return Path(sys.prefix) / "Lib" / "site-packages"
        else:
            version = sys.version_info
            return Path(sys.prefix) / "lib" / f"python{version.major}.{version.minor}" "site-packages"

    def _validate_type(self, type: str):
        if type not in PyinstDistType.list():
            raise ValueError(
                f"ValueError: Unsupported distribution type for target '{self.prog}', "
                f"'{type}' not in {PyinstDistType.list()}."
            )
        return PyinstDistType(type)

    def build(self):
        dist_path = Path("dist", "pyinstaller")

        PyInstaller.__main__.run(
            [
                str(self.source),
                self.type.pyinst_flags,
                "--name", self.prog,
                "--noconfirm",
                "--distpath", str(dist_path),
                "--specpath", str(dist_path / ".specs"),
                "--paths", str(self._site_packages),
                "--log-level=WARN",
                "--contents-directory", f"_{self.prog}_internal",
            ]
        )

    def bundle_wheel(self, io):
        wheels = glob.glob("*-py3-none-any.whl", root_dir="dist")
        for wheel in wheels:
            folder_to_add = Path("dist", "pyinstaller", self.prog)

            io.write_line(f"  - Adding <c1>{self.prog}</c1> to data scripts <debug>{wheel}</debug>")

            add_folder_to_wheel_data_script(folder_to_add, Path("dist", wheel))


class PyInstallerPlugin(ApplicationPlugin):
    _app: Application = None

    _targets: List[PyInstallerTarget]

    def __init__(self):
        self._targets = []

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
    def _use_bundle(self):
        return True in [t.bundled for t in self._targets]

    def activate(self, application: Application) -> None:
        """
        Activation method for ApplicationPlugin
        """
        self._app = application
        self._targets = self._parse_targets()

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

        wheels = glob.glob("*-py3-none-any.whl", root_dir="dist")
        if len(wheels) > 0:
            io.write_line(f"Replacing <info>platform</info> in wheels <b>({platform})</b>")
            for wheel in wheels:
                new = wheel.replace("-any.whl", f"-{platform}.whl")
                os.replace(Path("dist", wheel), Path("dist", new))
                io.write_line(f"  - {new}")

    def _build_binaries(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher) -> None:
        """
        Build binaries for every target with PyInstaller. Performed before wheel packaging.
        """
        command = event.command

        if not isinstance(command, BuildCommand):
            return

        io = event.io

        io.write_line(f"Building <c1>binaries</c1> with PyInstaller <c1>Python {sys.version}</c1>")

        for t in self._targets:
            io.write_line(
                f"  - Building <info>{t.prog}</info> <debug>{t.type.name}{' BUNDLED' if t.bundled else ''}</debug>"
            )
            t.build()
            io.write_line(
                f"  - Built <success>{t.prog}</success> "
                f"-> <success>'{Path('dist', 'pyinstaller', t.prog)}'</success>"
            )

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
