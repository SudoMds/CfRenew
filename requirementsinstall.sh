#!/bin/bash

# Update the package list
echo "Updating package list..."
sudo apt update

# Install Python packages via apt
echo "Installing system packages via apt..."
sudo apt install -y python3-aiohttp python3-grpclib python3-protobuf python3-cryptography python3-requests

# Install Python packages via pip3 with --break-system-packages
echo "Installing Python packages via pip with --break-system-packages..."
sudo pip3 install aiohttp grpclib protobuf cryptography pycryptodome requests --break-system-packages

# Confirm installation
echo "Installation complete. Verifying packages..."

python3 -c "import aiohttp, grpclib, google.protobuf, cryptography, Crypto, requests; print('All packages installed successfully!')"

if [ $? -eq 0 ]; then
    echo "All packages were installed and verified successfully."
else
    echo "There was an issue installing the packages."
fi
