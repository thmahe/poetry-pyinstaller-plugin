#!/bin/bash
set -ex

./dist/pyinstaller/manylinux*/package-directory/package-directory | grep "icon.ico exists"
./dist/pyinstaller/manylinux*/package-directory/package-directory | grep "icon_a.ico exists"
./dist/pyinstaller/manylinux*/package-directory/package-directory | grep "element_images/image.png exists"
./dist/pyinstaller/manylinux*/package-directory/package-directory | grep "element_images/image_a.png exists"

find ./dist/pyinstaller/manylinux*/package-directory/LICENSE
find ./dist/pyinstaller/manylinux*/package-directory/USER_README.md
find ./dist/pyinstaller/manylinux*/package-directory/docs/index.html
find ./dist/pyinstaller/manylinux*/package-directory/_package-directory_internal/icon.ico
find ./dist/pyinstaller/manylinux*/package-directory/_package-directory_internal/icon_a.ico
find ./dist/pyinstaller/manylinux*/package-directory/_package-directory_internal/element_images/image.png
find ./dist/pyinstaller/manylinux*/package-directory/_package-directory_internal/element_images/image_a.png

if [ -f ./dist/pyinstaller/manylinux*/package-directory/README ]; then
    echo "README shouldn't exist"
    exit 1
fi

echo "PASS"
