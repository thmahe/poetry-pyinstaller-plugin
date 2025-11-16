# SPDX-FileCopyrightText: Copyright 2024-2025 Thomas Mahé <oss@tmahe.fr>
# SPDX-License-Identifier: MIT

from __future__ import annotations

__author__ = "Thomas Mahé <oss@tmahe.fr>"

import fnmatch
import importlib
import logging
import os
from pathlib import Path
from typing import List, Optional

import poetry.console
from cleo.commands.command import Command
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND, TERMINATE
from cleo.events.console_terminate_event import ConsoleTerminateEvent
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.utils.env import EnvManager

from poetry_pyinstaller_plugin import Target, __version__, utils
from poetry_pyinstaller_plugin.hooks import PostHook, PreHook


class PyInstallerShowCommand(Command, utils.LoggingMixin):
    name = "pyinstaller show"
    description = "Print plugin version."

    def handle(self) -> int:
        self.log(f"poetry-pyinstaller-plugin {__version__}")
        return 0


class PyInstallerBuildCommand(BuildCommand, utils.LoggingMixin):
    name = "pyinstaller build"
    description = "Build PyInstaller targets (Excluding targets with bundle feature enabled)."
    targets: List[Target]
    output: Path

    def __init__(self, application: Application):  # pragma: nocover
        super().__init__()
        self._app = application
        self._pyproject = utils.PyProjectConfig(self._app.poetry.pyproject.data)
        self.attach_io(application._io)  # noqa

        targets = self._pyproject.lookup("tool.poetry-pyinstaller-plugin.targets", dict())

        self.targets = [Target(name, self._app.poetry, io=self._io) for name in targets.keys()]

        self.platform = utils.get_platform(self._app.poetry)
        self.pre_build_hook = None
        self.post_build_hook = None

        if hook_spec := self._pyproject.lookup('tool.poetry-pyinstaller-plugin.pre-build', None):
            self.pre_build_hook = PreHook(self._app, *hook_spec.split(":"))

        if hook_spec := self._pyproject.lookup('tool.poetry-pyinstaller-plugin.post-build', None):
            self.post_build_hook = PostHook(self._app, *hook_spec.split(":"))

    @property
    def use_bundle(self) -> bool:
        return True in [t.bundle for t in self.targets]

    def handle(self) -> int:  # pragma: nocover
        env_manager = EnvManager(self._app.poetry, io=self._io)
        venv = env_manager.create_venv()
        venv.run("poetry", "install", "--all-extras", "--all-groups")
        venv_version = f"python{venv.version_info[0]}.{venv.version_info[1]}"
        pyinstaller_version = venv.run("pyinstaller", "--version").strip()

        if self.pre_build_hook:
            self.pre_build_hook.attach_io(self._io)
            self.pre_build_hook._exec(venv)  # noqa

        self.log(f"Building <info>pyinstaller</info> <debug>[{venv_version} {self.platform}]</debug>")
        self.debug(f"PyInstaller version = {pyinstaller_version}")

        self.log(str(self._app.poetry.pyproject_path))

        if len(self.targets) == 0:
            self.warning("No targets definition found, nothing to build with pyinstaller.")

        for target in self.targets:
            target.build(self._app.poetry, self)

        if self.post_build_hook:
            self.post_build_hook.attach_io(self._io)
            self.post_build_hook._exec(venv)  # noqa

        return 0

    def bundle_wheels(self):  # pragma: nocover
        wheels = []
        output_path = utils.get_output_path(self)
        for file in os.listdir(output_path):
            if fnmatch.fnmatch(file, '*-py3-none-any.whl'):
                wheels.append(file)

        targets = list(filter(lambda t: t.bundle and not t.skip, self.targets))

        if len(targets) == 0:
            return

        self.log("Bundling PyInstaller targets to wheel(s)")
        for wheel in wheels:
            for target in targets:
                target.bundle_to_wheel(output_path, wheel)

        if len(wheels) > 0:
            self.log(f"Replacing <info>platform</info> in wheels <b>({self.platform})</b>")
            for wheel in wheels:
                new = wheel.replace("-any.whl", f"-{self.platform}.whl")
                os.replace(output_path / wheel, output_path / new)
                self.log(f"  - {new}")


class PyInstallerPlugin(ApplicationPlugin):
    _app: Application = None
    _pyproject: Optional[utils.PyProjectConfig] = None
    build_command: Optional[PyInstallerBuildCommand] = None

    def activate(self, application: poetry.console.application.Application) -> None:  # pragma: nocover
        """
        Activation method for ApplicationPlugin
        """
        self._app = application

        # Reload logging to attach PyInstaller to Poetry logging
        importlib.reload(logging)

        def build_command_factory():
            return PyInstallerBuildCommand(self._app)

        def show_command_factory():
            return PyInstallerShowCommand()

        application.command_loader.register_factory("pyinstaller build", build_command_factory)
        application.command_loader.register_factory("pyinstaller show", show_command_factory)

        application.event_dispatcher.add_listener(COMMAND, self.on_build_command)
        application.event_dispatcher.add_listener(TERMINATE, self.on_terminate)

    def on_terminate(self, event: Event, event_name: str, dispatcher: EventDispatcher) -> None:  # pragma: nocover
        if isinstance(event, ConsoleTerminateEvent) and event.command.name == "build":

            # Skip build if format specified in build command
            if event.io.input.option("format"):
                return

            if self.build_command and self.build_command.use_bundle:
                self.build_command.bundle_wheels()

    def on_build_command(self, event: Event, event_name: str, dispatcher: EventDispatcher) -> None:  # pragma: nocover
        """
        Main event
        """
        if isinstance(event, ConsoleCommandEvent) and event.command.name == "build":
            self.build_command = PyInstallerBuildCommand(self._app)

            # Skip build if format specified in build command
            if event.io.input.option("format"):
                return

            self.build_command.handle()
