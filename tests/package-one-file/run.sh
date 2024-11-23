#!/bin/bash
set -ex

./dist/pyinstaller/manylinux*/package-one-file | grep "icon.ico exists"
./dist/pyinstaller/manylinux*/package-one-file | grep "icon_a.ico exists"
./dist/pyinstaller/manylinux*/package-one-file | grep "element_images/image.png exists"
./dist/pyinstaller/manylinux*/package-one-file | grep "element_images/image_a.png exists"

find ./dist/pyinstaller/manylinux*/LICENSE
find ./dist/pyinstaller/manylinux*/USER_README.md
find ./dist/pyinstaller/manylinux*/docs/index.html

if [ -f ./dist/pyinstaller/manylinux*/README ]; then
    echo "README shouldn't exist"
    exit 1
fi

echo "PASS"
