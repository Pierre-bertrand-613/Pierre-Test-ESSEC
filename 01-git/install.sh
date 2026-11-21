#!/usr/bin/env bash
# Git mini exo - Part 7: a small installation script created on a feature branch.

echo "Starting installation..."

# Update the package lists (apt on Linux, brew on macOS)
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y tree
elif command -v brew >/dev/null 2>&1; then
    brew update
    brew install tree
else
    echo "No supported package manager found (apt-get or brew)."
    exit 1
fi

echo "Installation complete!"
