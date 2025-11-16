# Plugin Configuration

**Plugin options** are declared in `[tool.poetry-pyinstaller-plugin]` section of your `pyproject.toml` file.

Since release 2.x of `poetry-pyinstaller-plugin` **all** PyInstaller options 
are configurable at **target** or **plugin** level. 

**Order of precedence for options:** `target -> plugin -> default`


## Options

Are listed in this section, options that are **only** configurable at plugin level.

---

### `tool.poetry-pyinstaller-plugin.pre-build` { #pre-build data-toc-label="pre-build" }

Allow you to call a python function **before** the pyinstaller build.

```toml title="Example"
[tool.poetry-pyinstaller-plugin]
pre-build = "hooks.pyinstaller:post_build"
```

For more information about Hooks you can read [Reference > Hooks](../hooks/).

---

### `tool.poetry-pyinstaller-plugin.post-build` { #post-build data-toc-label="post-build" }

Allow you to call a python function **after** the pyinstaller build. 

```toml title="Example"
[tool.poetry-pyinstaller-plugin]
post-build = "hooks.pyinstaller:post_build"
```

For more information about Hooks you can read [Reference > Hooks](../hooks/).

## [Target Options](../target_configuration/)

As mentioned at the beginning of this page, **all** [target options](../target_configuration/) can be defined 
globally at plugin level and get effective to all targets (if not overridden at target level).

**Following given order of precedence:** `target -> plugin -> default`

```toml title="Option precedence example"
[tool.poetry-pyinstaller-plugin]
# Override default "onedir" build type for all targets
type = "onefile" 

[tool.poetry-pyinstaller-plugin.targets.my-tool]
source = "entrypoint.py"
# Override global option 'tool.poetry-pyinstaller-plugin.type'
type = "onedir"

[tool.poetry-pyinstaller-plugin.targets.my-tool-2]
source = "entrypoint.py"

# my-tool ---> "onedir" build as set in target config
# my-tool-2 -> "onefile" build as set in plugin config
```
