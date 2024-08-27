#!/bin/bash
owner="NohamR"
repo="GoFileCLI"
latest_release=$(curl -s https://api.github.com/repos/$owner/$repo/releases/latest)

tag_name=$(echo "$latest_release" | jq -r '.tag_name')
assets=$(echo "$latest_release" | jq -r '.assets[] | .name')

echo "Latest release tag: $tag_name"

OS=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS" == "darwin" ]]; then
    OS="osx"
fi

ARCH=$(uname -m)

if [[ "$ARCH" == "x86_64" ]]; then
    ARCH="x64"
elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

expected_file="GoFileCLI_${OS}-${ARCH}_*.tar.gz"

if [[ "$OS" == "windows" ]]; then
    expected_file="GoFileCLI_${OS}-${ARCH}_*.zip"
fi

selected_asset=$(echo "$assets" | grep -E "^GoFileCLI_${OS}-${ARCH}_.*")

if [[ -z "$selected_asset" ]]; then
    echo "No matching asset found for OS: $OS, Architecture: $ARCH"
    exit 1
fi

echo "Selected asset: $selected_asset"

download_url=$(echo "$latest_release" | jq -r --arg name "$selected_asset" '.assets[] | select(.name == $name) | .browser_download_url')

echo "Downloading $selected_asset from $download_url..."
curl -LO "$download_url"
if [[ ! -f "$selected_asset" ]]; then
    echo "Download failed."
    exit 1
fi

tar -xzf "$selected_asset"
extracted_dir=$(find . -type d -name "GoFileCLI*" | head -n 1)
if [[ -d "$extracted_dir" ]]; then
    sudo mv "$extracted_dir/gofilecli" /usr/local/bin/
    chmod +x /usr/local/bin/gofilecli
    echo "Installation completed. You can now use 'gofilecli'."
else
    echo "Failed to find the extracted directory."
    exit 1
fi

rm -rf "$selected_asset" "$extracted_dir"