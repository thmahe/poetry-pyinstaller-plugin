#!/bin/bash
set -ex

./dist/pyinstaller/manylinux*/hook/hook | grep "200"
./dist/pyinstaller/manylinux*/hook/hook | grep "Hello from 'my_package' included package"
./dist/pyinstaller/manylinux*/hook/hook | grep "Hello from 'my_package_b' included package"

find ./dist/post-build
find ./dist/post-build

echo "PASS"
