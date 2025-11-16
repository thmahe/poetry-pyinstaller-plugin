# SPDX-FileCopyrightText: Copyright 2025 Thomas Mahé <oss@tmahe.fr>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

from cleo.io.io import IO
from poetry.console.commands.build import BuildCommand
from poetry.core.masonry.builders.wheel import WheelBuilder
from poetry.poetry import Poetry
from tomlkit import TOMLDocument


class PyProjectConfig:
    def __init__(self, data: TOMLDocument):
        self.data = data

    def __eq__(self, other: PyProjectConfig):
        return self.data == other.data

    def lookup(self, field: str, default: Any = None) -> Any:
        if self.data:
            items = field.split('.')
            data = self.data

            if len(items) == 1:
                return data.get(field, default)

            for item in items[:-1]:
                data = data.get(item, {})
            return data.get(items[-1], default)

        raise RuntimeError("Error while retrieving pyproject.toml data.")

    def get_section(self, section: str) -> PyProjectConfig:
        return PyProjectConfig(self.lookup(section, {}))


class LoggingMixin:
    _io: IO

    def __init__(self, io: Optional[IO] = None, **kwargs):
        self._io = io

    def attach_io(self, io: IO):
        self._io = io

    def is_debug(self) -> bool:
        return self._io.is_debug()

    def log(self, msg: str) -> None:
        if self.is_debug():
            msg = f"<fg=yellow;options=bold>[poetry-pyinstaller-plugin]</> {msg}"
        self._io.write_line(msg)

    def warning(self, msg: str) -> None:
        self.log(f"<fg=yellow;options=bold>{msg}</>")

    def error(self, msg: str) -> None:
        self.log(f"<error>{msg}</error>")

    def debug(self, msg: str) -> None:
        if self.is_debug():
            self.log(f"<debug>{msg}</debug>")

    def debug_command(self, output: str):
        for line in output.splitlines():
            self.debug(f" + {line}")


def get_platform(poetry: Poetry) -> str:
    return WheelBuilder(poetry)._get_sys_tags()[0].split("-")[-1]  # noqa


def get_base_modules_path(poetry: Poetry) -> List[Path]:
    return [module.base for module in WheelBuilder(poetry)._module.includes]  # noqa


def get_output_path(command: BuildCommand) -> Path:
    # True when --output specified
    if dist_path := command.option("output"):  # noqa
        return Path(dist_path).resolve()
    else:
        return Path("dist").resolve()
