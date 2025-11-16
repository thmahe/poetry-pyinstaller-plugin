# Commands

Are listed on this page commands used/implemented by `poetry-pyinstaller-plugin` and solely exposed through
**Poetry CLI**.

## Poetry's Commands

### `poetry build`  { #poetry-build data-toc-label="build" }

Legacy build command provided by Poetry, PyInstaller targets are **always** build when format is unspecified.

```shell title="Example"
poetry build
```
```text title="Expected output (linux)"
Building pyinstaller [python3.12 manylinux_2_39_x86_64]
  - Building my-tool
  - Built my-tool
Building package_name (0.1.0)
Building sdist
  - Building sdist
  - Built package_name-0.1.0.tar.gz
Building wheel
  - Building wheel
  - Built package_name-0.1.0-py3-none-any.whl
```

!!! warning "Distributing bundled binaries in Wheels ?"

    Inclusion of executables in Wheel archives is only supported by this command.

---

## Plugin's Commands

### `poetry pyinstaller build` { #poetry-pyinstaller-build data-toc-label="build" }

Build PyInstaller targets only.

```shell title="Example"
poetry pyinstaller build
```
```text title="Expected output (linux)"
Building pyinstaller [python3.12 manylinux_2_39_x86_64]
  - Building my-tool
  - Built my-tool
```

---

### `poetry pyinstaller show` { #poetry-pyinstaller-show data-toc-label="show" }

Show installed version of `poetry-pyinstaller-plugin`.

```shell title="Example"
poetry pyinstaller show
```
```text title="Expected output (linux)"
poetry-pyinstaller-plugin x.x.x
```

## Debugging

### Logging

You can debug your PyInstaller builds by changing the logging level using legacy Poetry's `-v, --verbose` CLI option.

**Available logging levels:**

* `-v`: Set `--log-level=WARN`
* `-vv`: Set `--log-level=INFO`
* `-vvv`: Set `--log-level=DEBUG` **AND** `--debug=all`

!!! warning

    `--debug=all` option of PyInstaller enable debug logging in final executable.

### Build folder & Specs

Intermediate files created by PyInstaller during build are kept within your project under `build/<platform>/<target>` directory.

PyInstaller's `.spec` files are by default saved in `dist/pyinstaller/<platform>/.specs` directory.

!!! info

    Build folders are not re-used between builds to ensure repeatability of builds with clean & accurate dependency tree.
