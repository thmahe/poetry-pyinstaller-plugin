#!/bin/bash
set -ex

if [ -f ./dist/pyinstaller/manylinux*/one-file-internal ]; then
    false
fi

./dist/pyinstaller/manylinux*/one-file | grep "200"

echo "PASS"
