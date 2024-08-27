#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: No tag provided."
  echo "Usage: $0 <tag>"
  exit 1
fi

tag=$1

source ~/miniconda3/etc/profile.d/conda.sh
conda activate 310
python -m nuitka --standalone --assume-yes-for-downloads --output-dir=dist --static-libpython=no gofilecli.py 
mv dist/gofilecli.dist/gofilecli.bin ../gofilecli

date=$(date +"%Y%m%d")
tar cvzfp "GoFileCLI_linux-aarch64_${date}.tar.gz" gofilecli
gh release upload ${tag} "GoFileCLI_linux-aarch64_${date}.tar.gz"