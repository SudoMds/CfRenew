#!/bin/bash

# Update the package list
echo "Updating package list..."
sudo apt update

# Install make and Python packages via apt
echo "Installing system packages via apt..."
sudo apt install -y make python3-aiohttp python3-grpclib python3-protobuf python3-cryptography python3-requests

# Install Python packages via pip3 with --break-system-packages
echo "Installing Python packages via pip with --break-system-packages..."
sudo pip3 install aiohttp grpclib protobuf cryptography pycryptodome requests --break-system-packages

# Install GNU Parallel (version 20220515)
PARALLEL_VERSION="20220515"
echo "Installing GNU Parallel version $PARALLEL_VERSION..."
wget https://ftp.gnu.org/gnu/parallel/parallel-$PARALLEL_VERSION.tar.bz2

# Extract and install Parallel
tar -xvf parallel-$PARALLEL_VERSION.tar.bz2
cd parallel-$PARALLEL_VERSION
./configure
make
sudo make install

# Confirm installation of Parallel
parallel --version

if [ $? -eq 0 ]; then
    echo "GNU Parallel version $PARALLEL_VERSION installed successfully."
else
    echo "There was an issue installing GNU Parallel."
fi

# Confirm Python package installation
echo "Installation complete. Verifying Python packages..."

python3 -c "import aiohttp, grpclib, google.protobuf, cryptography, Crypto, requests; print('All Python packages installed successfully!')"

if [ $? -eq 0 ]; then
    echo "All Python packages were installed and verified successfully."
else
    echo "There was an issue installing the Python packages."
fi
