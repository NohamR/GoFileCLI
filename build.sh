#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: No tag provided."
  echo "Usage: $0 <tag>"
  exit 1
fi

tag=$1

source ~/miniconda3/etc/profile.d/conda.sh
conda activate 310
python -m nuitka --onefile --assume-yes-for-downloads --output-dir=dist --static-libpython=no gofilecli.py 
mv dist/dist/gofilecli.bin ./gofilecli

mkdir -p GoFileCLI_linux-arm64
mv ./gofilecli GoFileCLI_linux-arm64/

date=$(date +"%Y%m%d")
tar cvzfp "GoFileCLI_linux-arm64_${date}.tar.gz" GoFileCLI_linux-arm64

gh release upload ${tag} "GoFileCLI_linux-arm64_${date}.tar.gz"

rm -rf GoFileCLI_linux-arm64