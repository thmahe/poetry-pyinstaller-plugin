import os
import re
import subprocess
import sys
from pathlib import Path
from unittest import TestCase

platform = "not_set"


class TestOneFile(TestCase):

    def test_build(self):
        global platform
        project_path = Path("examples", "one-file").resolve()
        out = subprocess.run(("poetry", "build", "-vvv"), capture_output=True, cwd=project_path)

        try:
            self.assertEqual(out.returncode, 0)
        except AssertionError:
            raise RuntimeError(f"Error during build: {out.stdout.decode()}")

        self.assertIn(b"Building pyinstaller", out.stdout)
        self.assertIn(b"Built one-file", out.stdout)
        platform = str(re.findall(r"python.*\s(.*)]", out.stdout.decode()).pop())

    def test_exec(self):
        global platform
        bin_name = "one-file.exe" if "win32" == sys.platform else "one-file"
        bin_path = Path("examples", "one-file", "dist", "pyinstaller", platform, bin_name).resolve()
        out = subprocess.run(bin_path, capture_output=True)

        self.assertEqual(out.returncode, 0)
        self.assertEqual(f"Hello world !{os.linesep}".encode(), out.stdout)


class TestOneFileBundle(TestCase):
    def test_build(self):
        global platform
        project_path = Path("examples", "one-file-bundle").resolve()
        out = subprocess.run(("poetry", "build", "-vvv"), capture_output=True, cwd=project_path)

        try:
            self.assertEqual(out.returncode, 0)
        except AssertionError:
            raise RuntimeError(f"Error during build: {out.stdout.decode()}")

        self.assertIn(b"Building pyinstaller", out.stdout)
        self.assertIn(b"Built one-file", out.stdout)
        platform = str(re.findall(r"python.*\s(.*)]", out.stdout.decode()).pop())

    def test_exec(self):
        global platform

        bin_name = "one-file.exe" if "win32" == sys.platform else "one-file"
        bin_path = Path("examples", "one-file-bundle", "dist", "pyinstaller", platform, bin_name).resolve()
        out = subprocess.run(bin_path, capture_output=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(f"Hello world !{os.linesep}".encode(), out.stdout)
