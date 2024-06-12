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
```

If you are having troubles to install the plugin please refer to Poetry documentation: https://python-poetry.org/docs/plugins/#using-plugins

## Configuration

Are listed in this sections all options available to configure `poetry-pyinstaller-plugin` in your `pyproject.toml`

* `[tool.poetry-pyinstaller-plugin]`
  * `version` (string) 
    * Version of PyInstaller to use during build
    * Does not support version constraint
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
* `hiddenimport` (string, **default** `null`) : Hidden imports needed by the program (eg PIL._tkinter_finder for customtkinter).
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
