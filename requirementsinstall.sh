#!/bin/bash

# Update the package list
echo "Updating package list..."
sudo apt update

# Install make, jq, and Python packages via apt
echo "Installing system packages via apt..."
sudo apt install -y make jq python3-aiohttp python3-grpclib python3-protobuf python3-cryptography python3-requests

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

# Remove the downloaded file and extracted directory
cd ..
rm -rf parallel-$PARALLEL_VERSION parallel-$PARALLEL_VERSION.tar.bz2

# Confirm installation of Parallel and log versions
LOG_FILE="installed_packages.log"
echo "Logging installed package versions to $LOG_FILE..."

{
    echo "Installed Packages:"
    echo "=================="
    echo "GNU Parallel version:"
    parallel --version

    echo
    echo "System packages installed via apt:"
    dpkg -l | grep -E 'make|jq|python3-aiohttp|python3-grpclib|python3-protobuf|python3-cryptography|python3-requests'

    echo
    echo "Python packages installed via pip:"
    pip3 show aiohttp grpclib protobuf cryptography pycryptodome requests
} > $LOG_FILE

echo "Package installation log saved to $LOG_FILE."

# Confirm Python package installation
echo "Installation complete. Verifying Python packages..."

python3 -c "import aiohttp, grpclib, google.protobuf, cryptography, Crypto, requests; print('All Python packages installed successfully!')"

if [ $? -eq 0 ]; then
    echo "All Python packages were installed and verified successfully."
else
    echo "There was an issue installing the Python packages."
fi
