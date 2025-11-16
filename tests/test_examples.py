import re
import subprocess
from pathlib import Path
from unittest import TestCase

platform = "not_set"


class TestOneFile(TestCase):

    def test_build(self):
        global platform
        project_path = Path("examples", "one-file").resolve()
        out = subprocess.run(("poetry", "build"), capture_output=True, cwd=project_path)

        self.assertEqual(out.returncode, 0)

        self.assertIn(b"Building pyinstaller", out.stdout)
        self.assertIn(b"Built one-file", out.stdout)
        platform = str(re.findall(r"python.*\s(.*)]", out.stdout.decode()).pop())

    def test_exec(self):
        global platform
        bin_path = Path("examples", "one-file", "dist", "pyinstaller", platform, "one-file").resolve()
        out = subprocess.run(bin_path, capture_output=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(b"Hello world !\n", out.stdout)


class TestOneFileBundle(TestCase):
    def test_build(self):
        global platform
        project_path = Path("examples", "one-file-bundle").resolve()
        out = subprocess.run(("poetry", "build"), capture_output=True, cwd=project_path)

        self.assertEqual(out.returncode, 0)

        self.assertIn(b"Building pyinstaller", out.stdout)
        self.assertIn(b"Built one-file", out.stdout)
        platform = str(re.findall(r"python.*\s(.*)]", out.stdout.decode()).pop())

    def test_exec(self):
        global platform
        bin_path = Path("examples", "one-file-bundle", "dist", "pyinstaller", platform, "one-file").resolve()
        out = subprocess.run(bin_path, capture_output=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(b"Hello world !\n", out.stdout)
