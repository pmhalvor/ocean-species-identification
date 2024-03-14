#!/bin/bash

ROOT=$1

if [ ! -d "$ROOT/../HAT" ]; then
    cd "$ROOT/.."
    git clone https://github.com/XPixelGroup/HAT.git
    python3 -m pip install -e HAT -q

    # Remove conflicting files that are not needed
    rm HAT/hat/archs/discriminator_arch.py
    rm HAT/hat/archs/srvgg_arch.py
    rm HAT/hat/data/realesrgan_dataset.py
fi