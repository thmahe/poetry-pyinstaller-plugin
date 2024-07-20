# PyInstaller plugin for Poetry

Easily create executable binaries from your `pyproject.toml` using [PyInstaller](https://pyinstaller.org).

## Features
* **Multiple distribution formats**
  * **Single file** created in `dist` folder (executable archive)
  * **Folder** created in `dist` folder (containing executable and libraries)
  * **Bundled** executable in platform specific wheels as scripts
    * Both single file & folder distribution type can be bundled in wheels

## Installation

To install `poetry-pyinstaller-plugin` run the following command:
```shell
poetry self add poetry-pyinstaller-plugin
# or
pipx inject poetry poetry-pyinstaller-plugin
```

If you are having troubles to install the plugin please refer to Poetry documentation: https://python-poetry.org/docs/plugins/#using-plugins

## Configuration

Are listed in this sections all options available to configure `poetry-pyinstaller-plugin` in your `pyproject.toml`

* `[tool.poetry-pyinstaller-plugin]`
  * `version` (string) 
    * Version of PyInstaller to use during build
    * Does not support version constraint
  * `exclude-include` (boolean) 
    * Exclude poetry include. Default: `False`
  * `pre-build` (string)
    * Pre-build hook. `path.to.my.hook:pre-build-hook`
  * `post-build` (string)
    * Post-build hook. `path.to.my.hook:post-build-hook`
  * `use-poetry-install` (boolean) 
    * The default mode `False` installs packages (including "*pyinstaller*", "*certifi*" & "*cffi*") to the actual
      virtual environment by using internally pip. It will not use `poetry.lock` file, just the dependencies from the
      `pyproject.toml` configuration file.
    * When set to `True` the virtual environment should be completely installed by poetry including "*pyinstaller*"
      and optional "*certifi*" & "*cffi*" (for custom certificates).\
      This is done by adding them as dependencies to the `pyproject.toml` configuration file and run `poetry install`
      before starting `poetry build` command. Recommendation is the usage of an separate dependency group for
      pyinstaller.
  * `scripts` (dictionary) 
    * Where key is the program name and value a path to script or a `PyInstallerTarget` spec
    * Example: `prog-name = "my_package/script.py"`
  * `certifi` (dictionary)
    * `append` (list): List of certificates to include in `certifi.where()`
  * `collect` (dictionary)
    * `submodules` (list): Collect all submodules for specified package(s) or module(s)
    * `data` (list): Collect all data for specified package(s) or module(s)
    * `binaries` (list): Collect all binaries for specified package(s) or module(s)
    * `all` (list): Collect all submodules, data files, and binaries for specified package(s) or module(s)
  * `copy-metadata` (list) : list of packages for which metadata must be copied
  * `recursive-copy-metadata` (list) : list of packages for which metadata must be copied (including dependencies)
  * `include` (dictionary) : 
    * Data file(s) to include. `{source: destination}`
  * `package` (dictionary) : 
    * File(s) to include with executable. `{source: destination}`

`PyinstallerTarget` spec:
* `source` (string): Path to your program entrypoint
* `type` (string, **default:** `onedir`): Type of distribution format. Must be one of `onefile`, `onedir`
* `bundle` (boolean, **default:** `false`): Include executable binary onto wheel
* `noupx` (boolean, **default:** `false`) : Disable UPX archiving
* `strip` (boolean, **default** `false`) : Apply a symbol-table strip to the executable and shared libs (not recommended for Windows)
* `console` (boolean, **default** `false`) : Open a console window for standard i/o (default). On Windows this option has no effect if the first script is a ‘.pyw’ file.
* `windowed` (boolean, **default** `false`) : Windows and Mac OS X: do not provide a console window for standard i/o. On Mac OS this also triggers building a Mac OS .app bundle. On Windows this option is automatically set if the first script is a ‘.pyw’ file. This option is ignored on *NIX systems.
* `icon` (Path, **default** PyInstaller’s icon) : FILE.ico: apply the icon to a Windows executable. FILE.exe,ID: extract the icon with ID from an exe. FILE.icns: apply the icon to the .app bundle on Mac OS. Use “NONE” to not apply any icon, thereby making the OS to show some default
* `uac_admin` (boolean, **default** `false`) : Using this option creates a Manifest that will request elevation upon application start.
* `uac_uiaccess` (boolean, **default** `false`) : Using this option allows an elevated application to work with Remote Desktop.
* `argv_emulation` (boolean, **default** `false`) : Enable argv emulation for macOS app bundles. If enabled, the initial open document/URL event is processed by the bootloader and the passed file paths or URLs are appended to sys.argv.
* `arch` (string, **default** `null`) : Target architecture (macOS only; valid values: x86_64, arm64, universal2).
* `hiddenimport` (string | list), **default** `null`) : Hidden imports needed by the program (eg PIL._tkinter_finder for customtkinter).
* `runtime_hooks` (List[str], **default** `null`): One or more runtime hook paths to bundle with the executable. These hooks are executed before any other code or module to set up special features of the runtime environment.

### Examples

```toml
[tool.poetry-pyinstaller-plugin]
# Pyinstaller version (Optional, latest if not set)
# Does not support version constraint (eg: ^6.4)
version = "6.7.0"

# Disable UPX compression
disable-upx = true

# Include metadata from selected packages (including dependencies)
recursive-copy-metadata = [
    "requests"
]

# Include metadata from selected packages
copy-metadata = [
    "boto3"
]

[tool.poetry-pyinstaller-plugin.scripts]
hello-world = "my_package/main.py"
# Equivalent to
hello-world = { source = "my_package/main.py", type = "onedir", bundle = false }

# Single file bundled in wheel
single-file-bundled = { source = "my_package/main.py", type = "onefile", bundle = true}

# Folder bundled in wheel
folder-bundled = { source = "my_package/main.py", type = "onedir", bundle = true}

# Include a runtime hook
hook-example = { runtime_hooks = ['hooks/my_hook.py'], source = ... }

[tool.poetry-pyinstaller-plugin.certifi]
# Section dedicated to certifi, required if certificates must be included in certifi store
append = ['certs/my_cert.pem']

[tool.poetry-pyinstaller-plugin.collect]
# Collect all submodules, data files & binaries for 'package_A' and 'package_B'
all = ['package_A', 'package_B']
```

## Usage

Once configured `poetry-pyinstaller-plugin` is attached to the `poetry build` command.
```text
$ poetry build
Building binaries with PyInstaller Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0]
  - Building hello-world DIRECTORY
  - Built hello-world -> 'dist/pyinstaller/hello-world'
  - Building single-file-bundled SINGLE_FILE BUNDLED
  - Built single-file-bundled -> 'dist/pyinstaller/single-file-bundled'
  - Building folder-bundled DIRECTORY BUNDLED
  - Built folder-bundled -> 'dist/pyinstaller/folder-bundled'
Building my_package (0.0.0)
  - Building sdist
  - Built my_package-0.0.0.tar.gz
  - Building wheel
  - Built my_package-0.0.0-py3-none-any.whl
  - Adding single-file-bundled to data scripts my_package-0.0.0-py3-none-any.whl
  - Adding folder-bundled to data scripts my_package-0.0.0-py3-none-any.whl
Replacing platform in wheels (manylinux_2_35_x86_64)
  - my_package-0.0.0-py3-none-manylinux_2_35_x86_64.whl
```

### Build verbosity settings

Logging verbosity during PyInstaller build phase is configured through `poetry build` command using `--verbose/-v` option.

Available levels:
* `-v` : Set `--log-level=WARN`
* `-vv` : Set `--log-level=INFO`
* `-vvv` : Set `--log-level=DEBUG` & `--debug=all`
#### Example:
```text
$ poetry build --format pyinstaller -v
Using virtualenv: /home/.../.cache/pypoetry/virtualenvs/one-file-rP3OcWW--py3.10
  - Installing requests (>=2.32.3,<3.0.0)
Preparing PyInstaller 6.4.0 environment /home/.../.cache/pypoetry/virtualenvs/one-file-rP3OcWW--py3.10
Building binaries with PyInstaller Python 3.10 [manylinux_2_35_x86_64]
  - Building one-file SINGLE_FILE
      59 INFO: PyInstaller: 6.4.0, contrib hooks: 2024.7
      59 INFO: Python: 3.10.12
      60 INFO: Platform: Linux-6.5.0-41-generic-x86_64-with-glibc2.35
      60 INFO: wrote dist/pyinstaller/manylinux_2_35_x86_64/.specs/one-file.spec
      ...
      4009 INFO: Appending PKG archive to custom ELF section in EXE
      4020 INFO: Building EXE from EXE-00.toc completed successfully.
  - Built one-file -> 'dist/pyinstaller/manylinux_2_35_x86_64/one-file'
```

Expected directory structure:
```text
.
├── build ...................... PyInstaller intermediate build directory
│    ├── folder-bundled
│    ├── hello-world
│    └── single-file-bundled 
├── dist ....................... Result of `poetry build` command
│    ├── pyinstaller ............. PyInstaller output
│    │    ├── .specs/ ............ Specs files
│    │    ├── hello-world/
│    │    ├── folder-bundled/ 
│    │    └── single-file-bundled
│    ├── my_package-0.0.0-py3-none-manylinux_2_35_x86_64.whl ... Wheel with bundled binaries
│    └── my_package-0.0.0.tar.gz ............................... Source archive, binaries are never included
├── pyproject.toml
└── my_package
    ├── __init__.py
    └── main.py
```

## Dependencies notice

Major benefit of this plugin is to create dependency free wheels with executable binaries (including dependencies).

It is then recommended to include your dependencies as optional in your `pyproject.toml`

### Example
```toml
[tool.poetry]
name = "my-package"

[tool.poetry.dependencies]
python = "^3.8"
rich = {version = "^13.7.0", optional = true}

[tool.poetry.extras]
with-deps = ["rich"]
```

Resulting package will not require any dependency except if installed with extra `with-deps`.
```shell
# Installation without dependencies (included in executable binaries)
$ pip install my-package

# Installation with dependencies (If package imported as modules in another project)
$ pip install my-package[with-deps] 
```

Bundled binaries must be built with all dependencies installed in build environment.

## Packaging additional files

This plugin by default supports `tool.poetry.include`, but it can be disabled
for more control. You can also add files *next* to the executable by using the
`package` setting

### Example
```toml
[tool.poetry]
name = "my_project"
include = [
    { path = "README.md", format = ["sdist"] },
]

[tool.poetry-pyinstaller-plugin]
# Disable [tool.poetry.include] and use plugin settings instead
exclude-include = true

[tool.poetry-pyinstaller-plugin.scripts]
hello-world = "my_package/main.py"

[tool.poetry-pyinstaller-plugin.package]
# 1-1 next to executable
"README.md" = "."

# renaming next to executable
"user/README.md" = "USER_README.md"

# directory next to executable
"docs" = "."

[tool.poetry-pyinstaller-plugin.include]
# loose files in bundle
"icons/*" = "."

# entire directory in bundle
"images/*" = "element_images"
```

Expected directory structure:
```text
.
├── build ...................... PyInstaller intermediate build directory
├── dist ....................... Result of `poetry build` command
│    ├── pyinstaller ............. PyInstaller output
│    │    ├── .specs/ ............ Specs files
│    │    └── hello-world/
│    │          ├── docs/ ............ Packaged Docs
│    │          │     ├── how_to.md
│    │          │     └── if_breaks.md
│    │          ├── my_project_internal/ ............ Onedir bundle
│    │          │     ├── main_icon.svg ............... Included icon
│    │          │     ├── extra_icon.svg .............. Included icon
│    │          │     └── element_images/ ............. Included images
│    │          │           ├── footer_icon.svg
│    │          │           └── header_icon.svg
│    │          ├── my_project.exe ............ Bundled program
│    │          ├── README.md ................. Packaged Readme
│    │          └── USER_README.md. ........... Packaged User Readme
│    ├── my_package-0.0.0-py3-none-manylinux_2_35_x86_64.whl ... Wheel with bundled binaries
│    └── my_package-0.0.0.tar.gz ............................... Source archive, includes README.md
├── docs/
│    ├── how_to.md
│    └── if_breaks.md
├── user/
│    └── README.md
├── icons/
│    ├── main_icon.svg
│    └── extra_icon.svg
├── images/
│    ├── footer_icon.md
│    └── header_icon.svg
├── pyproject.toml
├── README.py
└── my_package
    ├── __init__.py
    └── main.py
```

## Hooks

The `pre-build` and `post-build` settings allow you to call a python function before and after the pyinstaller build. Each hook is passed a [hook interface](#hook_interface) class that allows access to Poetry, io and the virtual environment.

This lets you have further control in niche situations.

### Example
```toml
[tool.poetry]
name = "my_project"

[tool.poetry-pyinstaller-plugin]
# ran after requirements install and before builds
pre-build = "hooks.pyinstaller:post_build"

# ran after all builds are done
post-build = "hooks.pyinstaller:post_build"

[tool.poetry-pyinstaller-plugin.scripts]
hello-world = "my_package/main.py"

[tool.poetry-pyinstaller-plugin.package]
# package output from mkdocs
"site" = "docs"
```

<a name="hooks_pyinstaller"></a> **hooks/pyinstaller.py**:
```python
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

def pre_build(interface) -> None:
    """
    Pyinstaller pre build hook. Build local documentation.
    """
    interface.write_line("  - <b>Building local docs</b>")

    test_group = interface.poetry.package._dependency_groups["docs"]  # noqa: SLF001
    for req in test_group.dependencies:
        pip_r = req.base_pep_508_name_resolved.replace(" (", "").replace(
            ")", ""
        )
        interface.write_line(f"    - Installing <c1>{req}</c1>")
        interface.run_pip(
            "install",
            "--disable-pip-version-check",
            "--ignore-installed",
            "--no-input",
            pip_r,
        )

    interface.run("poetry", "run", "mkdocs", "build", "--no-directory-urls")
    interface.write_line("    - <fg=green>Docs built</>")

def post_build(interface) -> None:
    """
    Pyinstaller post build hook. Version built directory, remove generated folders.
    """
    dist_path = Path("dist", "pyinstaller", interface.platform)
    version = interface.pyproject_data["tool"]["poetry"]["version"]

    interface.write_line("  - <b>Visioning built</b>")
    for script in interface.pyproject_data["tool"]["poetry-pyinstaller-plugin"]["scripts"]:
        source = Path(dist_path, script)
        destination = Path(dist_path, f"{script}_{version}")

        if destination.exists():
            shutil.rmtree(destination)  # remove existing

        shutil.move(f"{source}", f"{destination}")
        interface.write_line(
            f"    - Updated "
            f"<success>{script}</success> -> "
            f"<success>{script}_{version}</success>"
        )

    interface.write_line("  - <b>Cleaning</b>")
    shutil.rmtree(Path("build"))
    interface.write_line("    - Removed build directory")
    shutil.rmtree(Path("site"))
    interface.write_line("    - Removed site directory")
```

<details>

<summary><a name="hook_interface"></a>Hook Interface</summary>

Here are the attributes and functions for the hook interface class, see example [hook file](#hooks_pyinstaller) for basic usage.

> Note: If using linter(s), placing this class in a `TYPE_CHECKING` block will remove *most* errors.

```python
from typing import Dict, List, Any

class PyIntallerHookInterface:
    """
    Pyinstaller hook interface

    Attributes:
        _io (IO): cleo.io.io IO instance
        _venv (VirtualEnv): poetry.utils.env VirtualEnv instance
        poetry (Poetry): poetry.poetry Poetry instance
        pyproject_data (dict): pyproject.TOML contents
        platform (str): platform string
    """

    poetry: Any
    pyproject_data: Dict
    platform: str

    def run(self, command: str, *args: str) -> None:
        """Run command in virtual environment"""

    def run_pip(self, *args: str) -> None:
        """Install requirements in virtual environment"""

    def write_line(self, output: str) -> None:
        """Output message with Poetry IO"""
```

</details>

