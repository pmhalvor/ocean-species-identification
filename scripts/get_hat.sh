#!/bin/bash

# set too to $1 if provided else use pwd
if [ -z "$1" ]; then
    ROOT=$(pwd)
else
    ROOT=$1
fi

if [ ! -d "$ROOT/../HAT" ]; then
    cd "$ROOT/.."
    git clone https://github.com/XPixelGroup/HAT.git
    python3 -m pip install -e HAT -q

    # Remove conflicting files that are not needed
    rm HAT/hat/archs/discriminator_arch.py
    rm HAT/hat/archs/srvgg_arch.py
    rm HAT/hat/data/realesrgan_dataset.py
fi