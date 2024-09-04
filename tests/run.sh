#!/bin/bash
set -e

for d in */ ; do
    echo "### $d ###"
    cd $d
    rm -rf build dist
    poetry build --format pyinstaller
    ./run.sh
    cd -
done
