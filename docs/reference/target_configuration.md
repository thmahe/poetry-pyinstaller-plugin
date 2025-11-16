# Target Configuration

**Target options** are specified in `[tool.poetry-pyinstaller-plugin.targets.<TARGET>]` section of `pyproject.toml`
file.
Where `<TARGET>` is the final executable name produced by PyInstaller.

Since release 2.x of `poetry-pyinstaller-plugin` **all** PyInstaller options
are configurable at **target** or **plugin** level.

**Order of precedence for options:** `target -> plugin -> default`

## Options

Are listed in this section, supported options allowing you to customize target build.

---

### source `path` ~_required_~ { #source data-toc-label="source" }

Path to your future executable entrypoint.

```toml title="Example - Minified form"
[tool.poetry-pyinstaller-plugin.targets]
my-tool = "my_package/entrypoint.py"
# or
my-tool = { source = "my_package/entrypoint.py" }
```

**Or**

```toml title="Example - Dedicated target block"
[tool.poetry-pyinstaller-plugin.targets.my-tool]
source = "my_package/entrypoint.py"
```

Above examples produces **identical** target specs, using dedicated target block is heavily recommended
to keep your `pyproject.toml` readable.

---

### type `str` { #type data-toc-label="type" }

Default: `onedir`

Type of PyInstaller distribution format.

* `onedir`: Create a one-folder bundle containing an executable
* `onefile`: Create a one-file bundled executable

---

### bundle `boolean` { #bundle data-toc-label="bundle" }

Default: `false`

Bundle executable to Wheels and register them as executable scripts.

---

### noupx `boolean` { #noupx data-toc-label="noupx" }

Default: `false`

Disable UPX archiving.

---

### strip `boolean` { #strip data-toc-label="strip" }

Default: `false`

Apply a symbol-table strip to the executable and shared libraries<br/>
**Not recommended for Windows**

---

### console `boolean` { #console data-toc-label="console" }

Default: `false`

Open a console window for standard IO (default).<br/>
This option has no effect in **Windows** if the first script is a `.pyw` file.

---

### windowed `boolean` { #windowed data-toc-label="windowed" }

Default: `false`

Windows and Mac OS X: do not provide a console window for standard IO.<br/>
On **macOS** this also triggers building a macOS `.app` bundle.<br/>
On **Windows** this option is automatically set if the first script is a `.pyw` file.

**This option is ignored on *NIX systems.**

---

### icon `path` { #icon data-toc-label="icon" }

Default: PyInstaller’s icon

Set the icon for executables.

* `FILE.ico` - Apply the icon to a Windows executable.
* `FILE.exe,ID` - Extract the icon with ID from an exe.
* `FILE.icns` - Apply the icon to the .app bundle on macOS.

Use `NONE` to not apply any icon, thereby making the OS to show system default.

### uac_admin `boolean` { #uac_admin data-toc-label="uac_admin" }

Default: `false`

Using this option creates a Manifest that will request elevation upon application start.

---

### uac_uiaccess `boolean` { #uac_uiaccess data-toc-label="uac_uiaccess" }

Default: `false`

Using this option allows an elevated application to work with Remote Desktop.

---

### argv_emulation `boolean` { #argv_emulation data-toc-label="argv_emulation" }

Default: `false`

Enable argv emulation for macOS app bundles.

If enabled, the initial open document/URL event is processed by the bootloader and the passed file paths or URLs are
appended to `sys.argv`.

---

### arch `str` ~macOS~ ~only~ { #arch data-toc-label="arch" }

Default: `null`

Target architecture. Accepted values: `x86_64`, `arm64`, `universal2`.

---

### hiddenimport `str | list[str]` { #hiddenimport data-toc-label="hiddenimport" }

Default: `null`

Hidden imports needed by the executable.

---

### runtime_hooks `list` { #runtime_hooks data-toc-label="runtime_hooks" }

Default: `null`

One or more runtime hook paths to bundle with the executable.

These hooks are executed before any other code or module to set up special features of the runtime environment.

---

### add_version `bool` { #add_version data-toc-label="add_version" }

Default: `false`

Suffix executable names with current package version. Dynamic versioning over `poetry-dynamic-versioning` plugin is supported.


These hooks are executed before any other code or module to set up special features of the runtime environment.

---


### when `str` { #when data-toc-label="when" }

Default: `null` - targets are always built.

Restrict build depending on package version. Possible values:

* `release`
* `prerelease`

---

### certifi.append `list[str]` { #certifi-append data-toc-label="certifi.append" }

Default: `[]`

List of certificates to include in certifi.where()

!!! warning

    `certifi` package must be registered in project dependencies if enabled.

---


### collect `dict[str, list[str]]` { #collect data-toc-label="collect" }

Default: `null`

Define which data from specific package or module must be included in final archive.

**Supported keys:**

* `submodules`: Collect all submodules for specified package(s) or module(s)
* `data`: Collect all data for specified package(s) or module(s)
* `binaries`: Collect all binaries for specified package(s) or module(s)
* `all`: Collect all submodules, data files, and binaries for specified package(s) or module(s)

---

### copy-metadata `list[str]` { #copy-metadata data-toc-label="copy-metadata" }

Default: `[]`

List of packages for which metadata must be copied.

---

### include `dict[Path, Path]` { #include data-toc-label="include" }

Default: `[]`

Data file(s) to include. `{source: destination}`

---

### package `dict[Path, Path]` { #package data-toc-label="package" }

Default: `[]`

File(s) to include with executable. `{source: destination}`

---

### exclude-include `boolean` { #exclude-include data-toc-label="exclude-include" }

Default: `false`

Disable `[tool.poetry.include]` and use plugin/target settings instead.

---

