#!/bin/bash
set -ex

./dist/pyinstaller/manylinux*/directory/directory | grep "200"
./dist/pyinstaller/manylinux*/directory/directory | grep "Hello from 'my_package' included package"
./dist/pyinstaller/manylinux*/directory/directory | grep "Hello from 'my_package_b' included package"

echo "PASS"
