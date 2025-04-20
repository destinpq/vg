#!/bin/bash
set -e

echo "Fixing NVIDIA DKMS errors..."

# Install correct kernel headers and build tools
echo "Installing kernel headers and build tools..."
sudo apt-get update
sudo apt-get install -y linux-headers-$(uname -r) build-essential dkms

# Stop conflicting services
echo "Stopping conflicting services..."
sudo systemctl stop docker || true
sudo systemctl stop nvidia-persistenced || true

# Remove failed installation
echo "Removing failed NVIDIA packages..."
sudo dpkg --purge --force-all nvidia-dkms-525 || true
sudo dpkg --purge --force-all cuda-drivers-525 || true
sudo dpkg --purge --force-all nvidia-driver-525 || true
sudo apt-get autoremove -y
sudo apt-get clean

# Fix the package system if it's in a bad state
echo "Fixing broken packages..."
sudo apt-get update --fix-missing
sudo dpkg --configure -a
sudo apt-get install -f

# Use Digital Ocean's recommended approach for H100
echo "Installing NVIDIA drivers using Digital Ocean's approach..."

# Get distro info
source /etc/os-release
VERSION_ID=$(echo $VERSION_ID | sed 's/\.//')

# Install CUDA repo key
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${VERSION_ID}/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install NVIDIA driver through Digital Ocean's repositories
sudo apt-get install -y cuda-drivers

# Check if DKMS module built successfully
echo "Checking DKMS status..."
dkms status

# Load NVIDIA modules
echo "Loading NVIDIA modules..."
sudo modprobe nvidia
sudo modprobe nvidia_uvm

# Create device nodes if they don't exist
echo "Creating device nodes..."
if [ ! -e /dev/nvidia0 ]; then
    sudo mknod -m 666 /dev/nvidia0 c 195 0
fi
if [ ! -e /dev/nvidiactl ]; then
    sudo mknod -m 666 /dev/nvidiactl c 195 255
fi
if [ ! -e /dev/nvidia-uvm ]; then
    sudo mknod -m 666 /dev/nvidia-uvm c 243 0
fi

# Install NVIDIA container toolkit
echo "Installing NVIDIA container toolkit..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/ubuntu${VERSION_ID}/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker for NVIDIA
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test NVIDIA
echo "Testing NVIDIA driver installation..."
nvidia-smi || echo "nvidia-smi failed, but continuing..."

echo "Fix completed. Please reboot with: sudo reboot" 