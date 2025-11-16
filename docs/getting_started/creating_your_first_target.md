# Creating your first target

## Project setup
Given this **very simple** project structure:
```text
.
├── src
│   └── package_name
│         └── main.py
├── pyproject.toml
└── README.md
```

```toml title="pyproject.toml"
[project]
name = "package_name"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.12,<3.15"

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.requires-plugins]
poetry-pyinstaller-plugin = { version = ">=2.0.0,<3.0.0" }

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[dependency-groups]
dev = [
    "pyinstaller (>=6.16.0,<7.0.0)"
]
```

```python title="main.py"
if __name__ == '__main__':
    print("Hello World !")
```

## Add target for pyinstaller

To add a new target, include following block to your `pyproject.yaml`:

```toml
[tool.poetry-pyinstaller-plugin.targets]
my-tool = "package_name/main.py"
```

## Build your target

To build your target, run the following command:
```shell
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

## Test your target

Build assets are stored within `dist/pyinstaller` directory under a platform specific directory.
Output directory might defer from this example.

Run from your project directory:
```shell
./dist/pyinstaller/<platform>/my-tool/my-tool
```
```text title="Expected output (linux)"
Hello World !
```
