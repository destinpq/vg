#!/bin/bash
set -e

echo "Installing NVIDIA drivers without DKMS (more reliable for Digital Ocean H100)..."

# Remove any existing NVIDIA installations
echo "Removing existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*'
sudo apt-get autoremove -y
sudo apt-get clean

# Fix package system
echo "Fixing package system..."
sudo apt-get update --fix-missing
sudo dpkg --configure -a
sudo apt-get install -f -y

# Install prerequisites
echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y build-essential linux-headers-$(uname -r) wget

# Install runfile drivers directly
echo "Downloading NVIDIA driver runfile (avoiding DKMS)..."
driver_version="525.147.05"
cuda_version="12.1.1"
wget https://developer.download.nvidia.com/compute/cuda/${cuda_version}/local_installers/cuda_${cuda_version}_${driver_version}_linux.run

# Make it executable
chmod +x cuda_${cuda_version}_${driver_version}_linux.run

# Stop potential conflicting services
sudo systemctl stop gdm || true
sudo systemctl stop lightdm || true
sudo systemctl stop docker || true
sudo systemctl stop nvidia-persistenced || true

# Install driver in silent mode, no kernel module, no DKMS
echo "Installing NVIDIA driver without DKMS..."
sudo ./cuda_${cuda_version}_${driver_version}_linux.run --silent --driver --no-opengl-libs --no-drm --no-man-page --override

# Clean up
rm cuda_${cuda_version}_${driver_version}_linux.run

# Set up environment variables
echo "Setting up environment variables..."
echo 'export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
source /etc/profile.d/cuda.sh

# Install NVIDIA container toolkit
echo "Installing NVIDIA container toolkit..."
source /etc/os-release
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/ubuntu${VERSION_ID}/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test NVIDIA driver
echo "Testing NVIDIA driver..."
nvidia-smi || echo "nvidia-smi failed. A reboot may be required."

echo "Installation completed. Please reboot with: sudo reboot" 