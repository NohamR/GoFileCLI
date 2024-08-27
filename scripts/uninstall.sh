#!/bin/bash

BINARY_NAME="gofilecli"

BINARY_PATH=$(which $BINARY_NAME)

if [[ -z "$BINARY_PATH" ]]; then
    echo "$BINARY_NAME is not installed or not found in PATH."
    exit 1
fi

echo "Found $BINARY_NAME at $BINARY_PATH."
read -p "Are you sure you want to uninstall $BINARY_NAME? [y/N]: " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

sudo rm -f "$BINARY_PATH"

if [[ ! -f "$BINARY_PATH" ]]; then
    echo "$BINARY_NAME has been successfully uninstalled."
else
    echo "Failed to uninstall $BINARY_NAME."
    exit 1
fi

echo "Checking for any leftover files or directories..."
leftovers=$(find /usr/local/bin -name "$BINARY_NAME" 2>/dev/null)

if [[ -n "$leftovers" ]]; then
    echo "Found leftover files:"
    echo "$leftovers"
    read -p "Do you want to remove these leftover files? [y/N]: " cleanup_confirm

    if [[ "$cleanup_confirm" == "y" || "$cleanup_confirm" == "Y" ]]; then
        sudo rm -rf $leftovers
        echo "Leftover files removed."
    else
        echo "Leftover files not removed."
    fi
fi

echo "Uninstallation complete."