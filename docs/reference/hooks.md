# Hooks

Hooks allow you to call a python function before and/or after the PyInstaller build.

Each hook is passed a hook object that allows access to Poetry, `pyproject.toml` data, logging methods and the
virtual environment.

This lets you have further control in niche situations.

!!! warning

    Hooks cannot be called from externaly managed package ! Ensure to have your hook module **aside of one of the package**
    managed by your Poetry project.
    
    For more information: [Poetry Documentation - The pyproject.toml file - packages](https://python-poetry.org/docs/pyproject/#packages)

## `PluginHook` Interface

### Attributes

|               Name | Type                     | Description                                      |
|-------------------:|--------------------------|--------------------------------------------------|
|           **type** | `Literal["pre", "post"]` | Type of hook once registered by Poetry           |
|           **name** | `str`                    | Hook's name as referenced in `pyproject.toml`    |
|         **poetry** | `poetry.poetry.Poetry`   | Poetry instance of current build                 |
| **pyproject_data** | `TOMLDocument`           | Parsed `pyproject.toml`, similar to a Dictionary |
|       **platform** | `str`                    | Name of the current platform                     |

### Private Attributes

|      Name | Type  | Description                            |
|----------:|-------|----------------------------------------|
| **_venv** | `Env` | `poetry.utils.env` VirtualEnv instance |
|   **_io** | `IO`  | `cleo.io.io` IO instance               |

!!! warning

    Before using private attributes please check available below methods.

    If something is missing, don't hesitate to raise your hand and log a new feature request !

### Methods

#### `PluginHook.run(command: str, *args: str) -> str` { #run-method data-toc-label="PluginHook.run" }

Run command in current Poetry environment, returns output of command.

|    Argument | Type  | Description           |
|------------:|-------|-----------------------|
| **command** | `str` | Command to run        |
|  **\*args** | `str` | Arguments for command |

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    hook.run("echo", "Hello world !")
```

---

#### `PluginHook.run_pip(*args: str) -> str` { #run-pip-method data-toc-label="PluginHook.run_pip" }

Run `pip` in current Poetry environment, returns output of command.

|   Argument | Type  | Description         |
|-----------:|-------|---------------------|
| **\*args** | `str` | Arguments for `pip` |

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    hook.run_pip("install", "requests")
```

---

#### `PluginHook.is_debug() -> bool` { #is-debug-method data-toc-label="PluginHook.is_debug" }

Returns `True` if current IO is running with debug enabled.

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    if hook.is_debug():
        hook.run_pip("install", "debug-package")
```

---

#### `PluginHook.log(msg: str) -> None` { #run-pip-method data-toc-label="PluginHook.log" }

Logs a message to current Poetry IO, displayed during `poetry build` execution.

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    hook.log("Hello world !")
```

---

#### `PluginHook.warning(msg: str) -> None` { #run-pip-method data-toc-label="PluginHook.warning" }

Logs warning message to current Poetry IO, displayed during `poetry build` execution.

**Message is displayed in bold yellow**

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    hook.warning("Warning: unable to...")
```

---

#### `PluginHook.error(msg: str) -> None` { #run-pip-method data-toc-label="PluginHook.error" }

Logs error message to current Poetry IO, displayed during `poetry build` execution.

**Message is displayed in bold red**

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    hook.error("Fatal error: unable to...")
```

---

#### `PluginHook.debug(msg: str) -> None` { #run-pip-method data-toc-label="PluginHook.debug" }

Logs debug message to current Poetry IO, displayed during `poetry build` execution.

**Message is only displayed when debug mode is enabled**

```python title="Example"
from poetry_pyinstaller_plugin import PluginHook


def my_hook(hook: PluginHook):
    hook.debug("Initializing hook...")
```

---

## Example

Start by registering your hooks as follows:

```toml title="pyproject.toml"
[tool.poetry-pyinstaller-plugin]
# ran after requirements install and before builds
pre-build = "hooks.pyinstaller:post_build"

# ran after all builds are done
post-build = "hooks.pyinstaller:post_build"

```

Basic hooks example:

```python title="hooks/pyinstaller.py"
from poetry_pyinstaller_plugin import PluginHook


def pre_build(hook: PluginHook):
    hook.log("Hello from pre-hook !")
    hook.warning("Oup ! Something went wrong, but it's OK !")
    hook.run("echo", "Hello world !")


def post_build(hook: PluginHook):
    hook.log("Hello from post-hook !")
    hook.debug("Debug message")
```

Test your hooks by either running `poetry build` or `poetry pyinstaller build`:

=== "Expected Output"

    ``` text
    Running pre-build hook 'hooks.pyinstaller:pre_build'
    Hello from pre-hook !
    Oup ! Something went wrong, but it's OK !
    Building pyinstaller [python3.12 manylinux_2_39_x86_64]
      - Building my-tool
    Running post-build hook 'hooks.pyinstaller:post_build'
    Hello from post-hook !
    ```

=== "With Debug Enabled `-vvv`"

    ``` text
    Running pre-build hook 'hooks.pyinstaller:pre_build'
    Hello from pre-hook !
    Oup ! Something went wrong, but it's OK !
    Running 'echo Hello world !'
    ++ Hello world !
    ++ 
    Building pyinstaller [python3.12 manylinux_2_39_x86_64]
    ...
    ...
    Running post-build hook 'hooks.pyinstaller:post_build'
    Hello from post-hook !
    Debug message
    ```
