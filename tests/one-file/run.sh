#!/bin/bash
set -ex

if [ ! -f ./dist/pyinstaller/manylinux*/one-file-with-version-1.0.4 ]; then
    false
fi

./dist/pyinstaller/manylinux*/one-file | grep "200"

echo "PASS"
