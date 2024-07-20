#!/bin/bash

for d in */ ; do
    echo "### $d ###"
    cd $d
    poetry build --format pyinstaller
    ./run.sh
    cd -
done
