#!/bin/bash
set -ex

./dist/pyinstaller/manylinux*/one-file-bundle | grep "200"

echo "PASS"
