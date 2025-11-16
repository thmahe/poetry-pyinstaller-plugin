# Getting Started

## Introduction

**Poetry PyInstaller Plugin** is a lightweight extension for [Poetry](https://python-poetry.org/) that makes packaging 
Python applications into standalone executables effortless.

It bridges the gap between Poetry’s dependency management and [PyInstaller](https://pyinstaller.org) binary packaging, 
letting you build distributable apps directly from your Poetry project without leaving the familiar poetry workflow.

With a single command, you can bundle your Python project (including all dependencies and metadata) into a platform-native executable, 
perfect for distribution to users without Python installed.

**Project Links**

* **PyPI Project:** [pypi.org - poetry-pyinstaller-plugin](https://pypi.org/project/poetry-pyinstaller-plugin/)
* **Source Code:** [github.com - thmahe/poetry-pyinstaller-plugin](https://github.com/thmahe/poetry-pyinstaller-plugin)
* **Issue Tracker:** [github.com - thmahe/poetry-pyinstaller-plugin/issues](https://github.com/thmahe/poetry-pyinstaller-plugin/issues)
* **Documentation:** [poetry-pyinstaller-plugin.tmahe.fr](http://poetry-pyinstaller-plugin.tmahe.fr/)

## Installation

=== "Poetry 2.x" 

    To install `poetry-pyinstaller-plugin` add the following section to your `pyproject.toml`

    ```toml title="pyproject.toml"
    [tool.poetry.requires-plugins]
    poetry-pyinstaller-plugin = { version = ">=2.0.0,<3.0.0", extras = ["plugin"] }
    ```
    
    **To complete the installation:**
    ```shell
    poetry add --group dev pyinstaller
    poetry install
    ```
    **Well done, your project is ready for pyinstaller builds !**

=== "Older releases"

    Depending on installation method, use one of the following command:
    
    ```shell title="Installed with pip or debian package"
    poetry self add poetry-pyinstaller-plugin
    ```
    *Or*
    
    ```shell title="Installed with pipx"
    pipx inject poetry poetry-pyinstaller-plugin
    ```
    
    **To complete the installation:**
    ```shell
    poetry add --group dev pyinstaller
    poetry install
    ```
    **Well done, your project is ready for pyinstaller builds !**

!!! info

    If you are having troubles installing the plugin please refer to [Poetry documentation - Using Plugins](https://python-poetry.org/docs/plugins/#using-plugins)


## Check plugin version

To check plugin installation you can run the following command:

```shell title="Shell"
$ poetry pyinstaller show
poetry-pyinstaller-plugin x.x.x
```
