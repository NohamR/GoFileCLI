# GoFileCLI :
......

# Installation :

## Set env variables :

Get API token from https://gofile.io/myProfile.
Copy folderId from a folder you own.

Windows :
```bash
setx GOPLOAD_TOKEN "XXXXXXX"
setx GOPLOAD_PRIVATE_PARENT_ID "UUID"
setx GOPLOAD_ACCOUNT_ID "UUID"
```

(Reluch Command Prompt to take effect)

Linux/MacOS :
```bash
export GOPLOAD_TOKEN="XXXXXXX"
export GOPLOAD_PRIVATE_PARENT_ID="UUID"
export GOPLOAD_ACCOUNT_ID="UUID"
```

# Usage :
Upload a file :
```bash
gofilecli -i 'file.txt'
```

# Compile on your own system :
```bash
git clone https://github.com/NohamR/GoFileCLI.git
apt install ccache patchelf
pip install nuitka
pip install -r requirements.txt
python -m nuitka --standalone --assume-yes-for-downloads --output-dir=dist --static-libpython=no gofilecli.py 
# dist/gofilecli.dist/gofilecli.bin
```

# To do :
- acc stats
- error-rateLimit
- env via CLI
- finish README.md
- download
- build + release
- chiffrer et dechiffrer les uploads