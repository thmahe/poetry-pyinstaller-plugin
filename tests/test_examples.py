import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import TestCase, skipIf


class _MetaExample(TestCase):
    name: str = None

    @property
    def platform(self) -> str:
        dist_path = Path("examples", self.name, "dist").resolve()
        return os.listdir(dist_path / "pyinstaller").pop()

    def setUp(self):
        if self.name is None:
            self.skipTest(reason="Example name not set.")

    def test_build(self):
        project_path = Path("examples", self.name).resolve()
        out = subprocess.run(("poetry", "build", "-vvv"), capture_output=True, cwd=project_path)
        build_stdout = out.stdout.decode()
        try:
            self.assertEqual(out.returncode, 0)
        except AssertionError:
            raise RuntimeError(f"Error during '{self.name}' build: {os.linesep}{build_stdout}")

        self.assertIn("Building pyinstaller", build_stdout)
        self.assertIn(f"Built {self.name}", build_stdout)

    def test_exec(self):
        bin_name = f"{self.name}.exe" if "win32" == sys.platform else self.name
        bin_path = Path("examples", self.name, "dist", "pyinstaller", self.platform, bin_name).resolve()
        out = subprocess.run(bin_path, capture_output=True)

        self.assertEqual(out.returncode, 0)
        self.assertEqual(f"Hello world !{os.linesep}".encode(), out.stdout)


class TestOneFile(_MetaExample):
    name = "one-file"


class TestOneFileBundle(_MetaExample):
    name = "one-file-bundle"
