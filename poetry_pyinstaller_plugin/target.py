# SPDX-FileCopyrightText: Copyright 2025 Thomas Mahé <oss@tmahe.fr>
# SPDX-License-Identifier: MIT

import dataclasses
import logging
import os
import textwrap
import zipfile
from errno import EEXIST, EINVAL, ENOTDIR
from pathlib import Path
from shutil import copy, copytree, rmtree
from typing import Any, Dict, List, Optional, Union

import tomlkit
from cleo.io.io import IO
from poetry.console.commands.build import BuildCommand
from poetry.core.version.pep440 import PEP440Version
from poetry.poetry import Poetry
from poetry.utils.env import Env, EnvManager
from tomlkit import TOMLDocument

from poetry_pyinstaller_plugin import utils


@dataclasses.dataclass(init=False)
class Target(utils.LoggingMixin):
    package_version: PEP440Version
    dist_path: Path
    work_path: Path
    platform: str
    prog: str
    source: Path
    type: str
    bundle: bool
    strip: bool
    no_upx: bool
    console: bool
    windowed: bool
    icon: Optional[str]
    uac_admin: bool
    uac_uiaccess: bool
    argv_emulation: bool
    arch: Optional[str]
    hidden_import: Union[str, List[str]]
    when: Optional[str]
    add_version: bool
    certificates: List[str]
    collect_config: Dict[str, List[str]]
    exclude_poetry_include: bool
    include_config: Dict[str, List[str]]
    runtime_hooks: List[str]
    copy_metadata_config: List[str]
    recursive_copy_metadata_config: List[str]
    package_config: Dict[str, str]

    def __init__(self, prog: str, poetry: Poetry, io: IO, **kwargs):
        super().__init__(io, **kwargs)
        self._global_config = utils.PyProjectConfig(poetry.pyproject.data)
        self._plugin_config = self._global_config.get_section("tool.poetry-pyinstaller-plugin")
        self._target_config = self._global_config.get_section(f"tool.poetry-pyinstaller-plugin.targets.{prog}")

        # When target specified by '<target> = "script.py"'
        if not isinstance(self._target_config.data, dict):
            self._target_config.data = TOMLDocument().add("source", self._target_config.data)

        self.prog = prog
        self.source = (poetry.pyproject_path.parent / self.lookup("source", None)).resolve()
        self.platform = utils.get_platform(poetry)
        self.package_version = self._get_package_version(poetry)
        self.work_path = (poetry.pyproject_path.parent / 'build' / self.platform).resolve()

        fields = {
            "type": "onedir",
            "bundle": False,
            "strip": False,
            "no-upx": False,
            "console": False,
            "windowed": False,
            "icon": None,
            "uac-admin": False,
            "uac-uiaccess": False,
            "argv-emulation": False,
            "arch": None,
            "hidden-import": None,
            "when": None,
            "add-version": False
        }
        for field, default in fields.items():
            self.__setattr__(field.replace("-", "_"), self.lookup(field, default))

        self.certificates = self.lookup("certifi.append", list())
        self.collect_config = self.lookup("collect", dict())
        self.exclude_poetry_include = self.lookup("exclude-poetry-include", False)
        self.include_config = self.lookup("include", dict())
        self.runtime_hooks = self.lookup("runtime-hooks", list())
        self.copy_metadata_config = self.lookup("copy-metadata", list())
        self.recursive_copy_metadata_config = self.lookup("recursive-copy-metadata", list())
        self.package_config = self.lookup("package", dict())

        if self.add_version:
            self.prog = f"{self.prog}-{self.package_version.to_string()}"

        self.validate()

    @property
    def pyinstaller_command(self) -> List[str]:
        args = [
            "pyinstaller",
            self.source,
            f"--{self.type}",
            "--name", self.prog,
            "--noconfirm",
            "--clean",
            "--workpath", self.work_path,
            "--distpath", self.dist_path,
            "--specpath", (self.dist_path / ".specs"),
            "--contents-directory", f"_{self.prog}_internal",
            "--strip" if self.strip else ...,
            "--no_upx" if self.no_upx else ...,
            "--console" if self.console else "--noconsole",
            "--windowed" if self.windowed else "--nowindowed",
            "--uac-admin" if self.uac_admin else ...,
            "--uac-uiaccess" if self.uac_uiaccess else ...,
            "--argv-emulation" if self.argv_emulation else ...,
        ]

        if self.icon:
            args.extend(("--icon", self.icon))

        if self.arch:
            args.extend(("--target-arch", self.arch))

        for hook in self.runtime_hooks:
            args.extend(("--runtime-hook", hook))

        for package in self.copy_metadata_config:
            args.extend(("--copy-metadata", package))

        for package in self.recursive_copy_metadata_config:
            args.extend(("--recursive-copy-metadata", package))

        self._add_collect_args(args)
        self._add_include_args(args)
        self._add_hidden_imports_args(args)
        self._add_logging_args(logging.root.level, args)

        args = list(filter(lambda i: i is not Ellipsis, args))
        return list(map(str, args))

    def _add_collect_args(self, args: List[Any]) -> None:
        for collect_type, modules in self.collect_config.items():
            if collect_type in ["submodules", "data", "binaries", "all"]:
                for module in modules:
                    args.extend((f"--collect-{collect_type}", module))

    def _add_include_args(self, args: List[Any]) -> None:
        sep = ";" if "win" in self.platform else ":"

        # Includes from poetry
        if not self.exclude_poetry_include:
            for item in self._global_config.lookup("tool.poetry.include", list()):
                if path := item if isinstance(item, str) else item.get("path", None):
                    args.extend(("--add-data", f"{Path(path).resolve()}{sep}."))

        # Includes from plugin
        for source, target in self.include_config.items():
            if source and target:
                args.extend(("--add-data", f"{Path(source).resolve()}{sep}{target}"))

    def _add_hidden_imports_args(self, args: List[Any]) -> None:
        if self.hidden_import:
            if isinstance(self.hidden_import, str):
                self.hidden_import = [self.hidden_import]
            for item in self.hidden_import:
                args.extend(("--hidden-import", item))

    def _add_logging_args(self, level: int, args: List[Any]) -> None:
        if level == logging.WARNING:
            args.append("--log-level=WARN")
        if level == logging.INFO:
            args.append("--log-level=INFO")
        if level == logging.DEBUG:
            args.extend(("--debug=all", "--log-level=DEBUG"))

    def _get_package_version(self, poetry: Poetry):
        # version from 'project.version'
        version = self._global_config.lookup("project.version", None)

        # version from 'tool.poetry.version'
        version = self._global_config.lookup("tool.poetry.version", version)

        # version from 'poetry-dynamic-versioning'
        if self._global_config.lookup("tool.poetry-dynamic-versioning.enable", False):  # pragma: nocover
            from poetry_dynamic_versioning import _get_config, _get_version
            pyproject = tomlkit.parse(poetry.pyproject_path.read_bytes().decode("utf-8"))
            version, _ = _get_version(_get_config(pyproject))

        return PEP440Version.parse(version)

    def validate(self):
        if self.type not in ["onefile", "onedir"]:
            raise ValueError(
                f"ValueError: Unsupported distribution type for target '{self.prog}', "
                f"'{self.type}' not in ['onefile', 'onedir']."
            )

        if self.when not in [None, "release", "prerelease"]:
            raise ValueError(
                f"ValueError: Unsupported value for field 'when' for target '{self.prog}', "
                f"'{self.when}' not in ['release', 'prerelease']."
            )

    def lookup(self, field: str, default: Any) -> Any:
        return self._target_config.lookup(field, self._plugin_config.lookup(field, default))

    @property
    def skip(self):
        if self.when == "release":
            return self.package_version.is_unstable()
        if self.when == "prerelease":
            return self.package_version.is_stable()
        return False

    def build(self, poetry: Poetry, command: BuildCommand):
        env_manager = EnvManager(poetry, io=self._io)
        venv = env_manager.create_venv()

        self.dist_path = utils.get_output_path(command) / "pyinstaller" / self.platform

        if self.skip:
            self.warning(f" <info>-</info> Skipping {self.prog} (on {self.when} only)")
            return

        self.log(f"  - Building <c1>{self.prog}</c1>")

        # Install dependencies
        self._install_dependencies(venv)

        # Deploy certificates to venv
        self._deploy_certificates(poetry, venv)

        # Run pyinstaller
        self._run_pyinstaller(venv)

        self.log(f"  - Built <success>{self.prog}</success>")

    def _install_dependencies(self, venv: Env):
        args = ("poetry", "install", "--all-extras", "--all-groups")
        self.debug(f"run '{' '.join(args)}'")
        self.debug_command(venv.run(*args))

    def _deploy_certificates(self, poetry: Poetry, venv: Env):
        for crt in self.certificates:
            crt_path = (poetry.pyproject_path.parent / crt).relative_to(poetry.pyproject_path.parent)
            self.log(f"  - Adding <c1>{crt_path}</c1> to certifi")
            venv.run_python_script(textwrap.dedent(f"""
            import certifi
            print(certifi.where())
            with open(r"{crt_path}", "r") as include:
                with open(certifi.where(), 'a') as cert:
                    cert.write(include.read())
            """))

    def _run_pyinstaller(self, venv: Env):
        args = self.pyinstaller_command
        self.debug(f"run '{' '.join(args)}'")
        self.debug_command(venv.run(*args))

    def _run_package(self):  # pragma: nocover
        if self.type == "onefile":
            package_path = Path("dist", "pyinstaller", self.platform, self.prog)
        else:
            package_path = Path("dist", "pyinstaller", self.platform)

        for source, target in self.package_config.items():
            destination = Path(package_path / (target if target != "." else source))
            try:
                if destination.exists() and destination.is_dir():
                    rmtree(destination)
                copytree(source, destination)
            except OSError as exc:  # python >2.5 or, is file and/or file exists
                if exc.errno in (ENOTDIR, EINVAL, EEXIST):
                    copy(source, destination)
                else:
                    raise

    def bundle_to_wheel(self, output_path: Path, wheel: str):  # pragma: nocover
        target_path = output_path / "pyinstaller" / self.platform / self.prog
        wheel_path = output_path / wheel

        self.log(f"  - Adding <c1>{self.prog}</c1> to data scripts <debug>{wheel}</debug>")
        with zipfile.ZipFile(wheel_path, "a", zipfile.ZIP_DEFLATED) as wheel_f:
            for wheel_file in wheel_f.filelist:
                if "dist-info/WHEEL" in wheel_file.filename:
                    wheel_scripts_path = Path(wheel_file.filename.replace("dist-info/WHEEL", "data/scripts/"))

            if os.path.isfile(target_path):
                wheel_f.write(target_path, arcname=wheel_scripts_path / target_path.name)
                return

            for root, dirs, files in os.walk(target_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    wheel_f.write(file_path, arcname=wheel_scripts_path / os.path.relpath(file_path, target_path))
