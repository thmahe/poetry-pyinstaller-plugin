# SPDX-FileCopyrightText: Copyright 2025 Thomas Mahé <oss@tmahe.fr>
# SPDX-License-Identifier: MIT

import importlib.util
import os
from pathlib import Path
from typing import Callable, Literal, Optional

from poetry.console.application import Application
from poetry.poetry import Poetry
from poetry.utils.env import Env
from tomlkit import TOMLDocument

from poetry_pyinstaller_plugin import utils


class PluginHook(utils.LoggingMixin):
    _venv: Env
    _hook: Optional[Callable]
    type: Literal["pre", "post"]
    name: str
    poetry: Poetry
    pyproject_data: TOMLDocument
    platform: str

    def __init__(self, application: Application, module_name: str, callable_name: str):
        super().__init__(application._io)  # noqa
        self.name = f"{module_name}:{callable_name}"
        self.poetry = application.poetry
        self.pyproject_data = self.poetry.pyproject.data
        self.platform = utils.get_platform(self.poetry)
        self._hook = self._get_callable(module_name, callable_name)

    def _get_source_path(self, module_name: str) -> Path:
        parts = module_name.split('.')

        for base_module in utils.get_base_modules_path(self.poetry):
            source = base_module / Path(*parts[:-1]) / f"{parts[-1]}.py"
            if source.exists():
                return source

        raise RuntimeError(f"Unable to find module '{module_name}' in current project.")

    def _get_callable(self, module_name: str, callable_name: str) -> Optional[Callable]:
        top_module = module_name.split(".")[-1]
        source_path = self._get_source_path(module_name)

        spec = importlib.util.spec_from_file_location(top_module, source_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, callable_name):
            return getattr(module, callable_name)

        return None

    def _exec(self, venv: Env) -> None:
        """
        Start hook callable
        """
        self._venv = venv
        if self._hook:
            self.log(f"<info>Running<info> {self.type}-build hook <debug>'{self.name}'</debug>")
            self._hook(self)
        else:
            module, _callable = self.name.split(':')
            self.warning(f"Skipping {self.type}-build hook, '{_callable}' callable not found in {module}.")

    def run(self, command: str, *args: str) -> str:
        """
        Run command in virtual environment
        """
        self.debug(f"Running '{command} {' '.join(args)}'")
        output = self._venv.run(command, *args)
        for line in output.split(os.linesep):
            self.debug("++ " + line)
        return output

    def run_pip(self, *args: str) -> str:
        """
        Install requirements in virtual environment
        """
        self.debug(f"Running 'pip {' '.join(args)}'")
        output = self._venv.run_pip(*args)
        for line in output.split(os.linesep):
            self.debug("++ " + line)
        return output


class PreHook(PluginHook):
    type = "pre"


class PostHook(PluginHook):
    type = "post"
