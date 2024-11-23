from datetime import datetime
from pathlib import Path


def pre_build(interface) -> None:
    interface.write_line("  - <b>adding pre-build file</b>")
    Path.mkdir(Path("dist"))
    with Path.open(Path("dist/pre-build"), "a") as f:
        f.write(f"pre-build: {datetime}")


def post_build(interface) -> None:
    interface.write_line("  - <b>adding post-build file</b>")
    with Path.open(Path("dist/post-build"), "a") as f:
        f.write(f"post-build: {datetime}")

