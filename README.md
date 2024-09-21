# GoFileCLI :
Upload or download a file to GoFile.

# Install :

- Linux/MacOS :
```bash
curl -fsSL https://raw.githubusercontent.com/NohamR/GoFileCLI/main/scripts/install.sh | sudo bash
```

- Windows :
Grab latest release from [releases](https://github.com/NohamR/GoFileCLI/releases/latest)

- Build on your own system :
```bash
git clone https://github.com/NohamR/GoFileCLI.git
apt install ccache patchelf
pip install nuitka
pip install -r requirements.txt
python -m nuitka --onefile --assume-yes-for-downloads --output-dir=dist --static-libpython=no gofilecli.py 
# dist/gofilecli.bin
```

## Set env variables :

Get API token from https://gofile.io/myProfile.
Copy folderId from a folder you own.

- Set up a .env based on [.env.example](.env.example)


- Linux/MacOS :
```bash
export GOPLOAD_TOKEN="XXXXXXX"
export GOPLOAD_PRIVATE_PARENT_ID="UUID"
export GOPLOAD_ACCOUNT_ID="UUID"
```

- Windows :
```bash
setx GOPLOAD_TOKEN "XXXXXXX"
setx GOPLOAD_PRIVATE_PARENT_ID "UUID"
setx GOPLOAD_ACCOUNT_ID "UUID"
```
(Reluch Command Prompt to take effect)

# Usage :
```bash
gofilecli -i 'file.txt' # to upload a file
gofilecli -f folder/ # to upload a folder
gofilecli -s # to get stats of your account
gofilecli -d https://gofile.io/d/XXXXX # to download a folder
```

# To do :
- KeyboardInterrupt + Lost connexion
- error-rateLimit
- env via CLI
- finish README.md
- chiffrer & dechiffrer uploads