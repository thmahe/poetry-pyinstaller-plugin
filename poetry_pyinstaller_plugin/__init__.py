# MIT License
#
# Copyright (c) 2024 Thomas Mahé <contact@tmahe.dev>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = "Thomas Mahé <contact@tmahe.dev>"

import os
import platform
import sys
import zipfile
from pathlib import Path

from poetry.core.packages.dependency import Dependency


def add_folder_to_wheel_data_script(folder_path: Path, wheel_path: Path) -> None:
    """
    Add a directory to a pre-built wheel
    :param folder_path: Directory to include
    :param wheel_path: Path to wheel
    :return: None
    """
    with zipfile.ZipFile(wheel_path, "a", zipfile.ZIP_DEFLATED) as wheelf:
        for e in wheelf.filelist:
            if "dist-info/WHEEL" in e.filename:
                data_script = Path(e.filename.replace("dist-info/WHEEL", "data/scripts/"))

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = data_script / os.path.relpath(file_path, folder_path)
                wheelf.write(file_path, arcname=arcname)

def validate_dependency(requirement: Dependency):
    return requirement.marker.validate({
        "sys_platform": sys.platform,
        "platform_machine": platform.machine(),
        "platform_python_implementation": platform.python_implementation(),
        "platform_release": platform.release(),
        "platform_system": platform.system(),
        "platform_version": platform.version(),
        "python_version": '.'.join(platform.python_version_tuple()[:2]),
        "python_full_version":    platform.python_version(),
        "implementation_name":    sys.implementation.name,
        "implementation_version": format_full_version(sys.implementation.version) if hasattr(sys, 'implementation') else "0",
    })

def format_full_version(info):
    version = '{0.major}.{0.minor}.{0.micro}'.format(info)
    kind = info.releaselevel
    if kind != 'final':
        version += kind[0] + str(info.serial)
    return version
