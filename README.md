# Installation :

## Set env variables :

Get API token from https://gofile.io/myProfile.
Copy folderId from a folder you own.

Windows :
```bash
setx GOPLOAD_TOKEN "XXXXXXX"
setx GOPLOAD_PRIVATE_PARENT_ID "UUID"
```

(Reluch Command Prompt to take effect)

Linux/MacOS :
```bash
export GOPLOAD_TOKEN="XXXXXXX"
export GOPLOAD_PRIVATE_PARENT_ID="UUID"
```

# Usage :
Upload a file :
```bash
gocli -i 'file.txt'
````

# To do :
- acc stats
- error-rateLimit
- env via CLI
- finish README.md
- download
- build + release
- chiffrer et dechiffrer les uploads