#!/bin/bash
set -ex

./dist/pyinstaller/manylinux*/one-file | grep "200"

echo "PASS"
