#!/bin/bash
set -ex

if [ -f ./dist/pyinstaller/manylinux*/one-file ]; then
    false
fi

./dist/pyinstaller/manylinux*/one-file-internal | grep "200"

echo "PASS"
